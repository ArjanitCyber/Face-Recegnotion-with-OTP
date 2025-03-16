import cv2 
import face_recognition
import numpy as np
import os
import time
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from PIL import Image, ImageTk   
import pyotp  #otp
import qrcode  #qr code

KNOWN_FACES_DIR = 'known_faces'
USER_SECRETS_FILE = 'user_secrets.txt'

if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)

class FaceRecognitionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Face Recognition App")
        self.master.geometry("800x600")
        self.master.config(bg="#f0f0f0")

        # Label to display the logged-in user at the top-right
        self.logged_in_user_label = tk.Label(master, text="No user logged in", font=("Arial", 12), bg="#f0f0f0", fg="black")
        self.logged_in_user_label.place(x=600, y=10)  # Position at the top-right

        # Buttons for Register and Login
        self.register_button = tk.Button(master, text="Register", command=self.start_register, font=("Arial", 14),
                                         bg="#4CAF50", fg="white", relief="raised", width=15)
        self.register_button.pack(pady=20)

        self.login_button = tk.Button(master, text="Login", command=self.start_login, font=("Arial", 14),
                                      bg="#E91E63", fg="white", relief="raised", width=15)
        self.login_button.pack(pady=20)

        # Admin button for account management
        self.admin_button = tk.Button(master, text="Admin", command=self.show_admin_window, font=("Arial", 12),
                                      bg="#FF5722", fg="white", relief="raised", width=10)
        self.admin_button.place(x=10, y=10)  # Place the button at the top-left corner

        # Video feed placeholder
        self.video_frame = tk.Label(master)
        self.video_frame.pack(pady=20)

        self.video_source = 0
        self.known_face_encodings = []
        self.known_face_names = []
        self.recognized_user = None
        self.video_capture = cv2.VideoCapture(self.video_source)

        self.user_secrets = self.load_user_secrets()
        self.load_known_faces()

        # Start live camera feed
        self.update_video_feed()

        self.face_verified = False  # Flag to indicate if the face is verified
        self.start_time = None  # Timer for face verification timeout

        self.logged_in = False  # Track if a user is logged in

    def load_known_faces(self):
        for filename in os.listdir(KNOWN_FACES_DIR):
            if filename.endswith('.jpg'):
                img_path = os.path.join(KNOWN_FACES_DIR, filename)
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(os.path.splitext(filename)[0])

    def load_user_secrets(self):
        if os.path.exists(USER_SECRETS_FILE):
            with open(USER_SECRETS_FILE, 'r') as file:
                return dict(line.strip().split('=') for line in file)
        return {}

    def save_user_secrets(self):
        with open(USER_SECRETS_FILE, 'w') as file:
            for user, secret in self.user_secrets.items():
                file.write(f"{user}={secret}\n")

    def generate_qr_code(self, username, secret):
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="FaceRecApp")
        qr = qrcode.make(uri)
        qr.show()

    def start_register(self):
        username = simpledialog.askstring("Register", "Enter your name:")
        if not username:
            messagebox.showerror("Error", "Name is required for registration.")
            return

        if username in self.user_secrets:
            messagebox.showerror("Error", "User already registered.")
            return

        # Generate an authenticator code
        secret = pyotp.random_base32()
        self.user_secrets[username] = secret
        self.save_user_secrets()
        self.generate_qr_code(username, secret)

        # Register face with live feedback
        messagebox.showinfo("Info", "Now registering your face. Look at the camera.")
        self.recognized_user = username
        self.register_face()

    def register_face(self):
        face_registered = False  # Flag to indicate if the face has been registered

        # Capture frames for registration
        for _ in range(30):  # Limit the number of frames processed for registration
            ret, frame = self.video_capture.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            # Check if any faces were detected
            if len(face_locations) == 0:
                cv2.putText(frame, "No face detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                # Draw a rectangle around detected faces
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Register the first detected face
                if not face_registered:
                    face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]  # Encode the first face
                    if face_encoding is not None:
                        img_path = os.path.join(KNOWN_FACES_DIR, f"{self.recognized_user}.jpg")
                        cv2.imwrite(img_path, frame)  # Save the first detected face image
                        self.known_face_encodings.append(face_encoding)
                        self.known_face_names.append(self.recognized_user)
                        face_registered = True  # Mark the face as registered

            # Display video feed with face rectangle
            self.display_video_frame(frame)

            if face_registered:
                break

        if face_registered:
            messagebox.showinfo("Success", f"Face successfully registered for '{self.recognized_user}'.")
        else:
            messagebox.showerror("Error", "No face detected during registration. Please try again.")

    def start_login(self):
        username = simpledialog.askstring("Login", "Enter your name:")
        if not username:
            messagebox.showerror("Error", "Name is required for login.")
            return

        if username not in self.user_secrets:
            messagebox.showerror("Error", "User not registered.")
            return

        # Verify the authenticator code
        otp = simpledialog.askstring("2FA", "Enter the code from your authenticator app:")
        totp = pyotp.TOTP(self.user_secrets[username])
        if not totp.verify(otp):
            messagebox.showerror("Error", "Invalid authenticator code.")
            return

        # Perform face recognition with live feedback
        messagebox.showinfo("Info", "Look at the camera for face verification.")
        self.recognized_user = username
        self.verify_face()

    def verify_face(self):
        self.face_verified = False  # Flag to indicate if the face is verified
        self.start_time = time.time()  # Set the start time for timeout check

        # Start a separate thread for face recognition
        self.master.after(100, self.check_for_face_recognition)

    def check_for_face_recognition(self):
        ret, frame = self.video_capture.read()
        if not ret:
            self.master.after(100, self.check_for_face_recognition)
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        user_verified = False
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            if True in matches:
                first_match_index = matches.index(True)
                if self.known_face_names[first_match_index] == self.recognized_user:
                    user_verified = True
                    break

        # Draw rectangles and display user name if recognized
        for (top, right, bottom, left) in face_locations:
            color = (0, 255, 0) if user_verified else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            label = self.recognized_user if user_verified else "Unknown"
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        # Display video frame with face rectangle
        self.display_video_frame(frame)

        # Check for timeout (10 seconds)
        if time.time() - self.start_time > 10:
            if not user_verified:
                messagebox.showerror("Error", "Face recognition timed out.")
                return

        if user_verified and not self.face_verified:
            self.face_verified = True
            messagebox.showinfo("Success", f"Welcome, {self.recognized_user}!")
            self.logged_in = True
            self.update_login_logout_buttons()
            self.update_logged_in_user_label()

        if not self.face_verified:
            self.master.after(100, self.check_for_face_recognition)

    def display_video_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_tk = ImageTk.PhotoImage(frame_pil)

        # Update the Tkinter image on the label
        self.video_frame.config(image=frame_tk)
        self.video_frame.image = frame_tk

    def update_video_feed(self):
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_tk = ImageTk.PhotoImage(frame_pil)

            # Update the Tkinter image on the label
            self.video_frame.config(image=frame_tk)
            self.video_frame.image = frame_tk

        self.master.after(10, self.update_video_feed)

    def update_login_logout_buttons(self):
        if self.logged_in:
            self.login_button.config(text="Log Out", command=self.logout)
        else:
            self.login_button.config(text="Login", command=self.start_login)

    def logout(self):
        self.logged_in = False
        self.recognized_user = None
        self.face_verified = False
        self.update_login_logout_buttons()
        self.update_logged_in_user_label()
        messagebox.showinfo("Logged Out", "You have been logged out.")

    def update_logged_in_user_label(self):
        if self.logged_in:
            self.logged_in_user_label.config(text=f"Logged in as: {self.recognized_user}")
        else:
            self.logged_in_user_label.config(text="No user logged in")

    def show_admin_window(self):
        password = simpledialog.askstring("Admin Login", "Enter password:")
        if password != "root":
            messagebox.showerror("Error", "Incorrect password.")
            return

        # Create a new window for account management
        admin_window = Toplevel(self.master)
        admin_window.title("Admin - Account Management")
        admin_window.geometry("400x300")

        # Listbox to show registered users
        listbox = tk.Listbox(admin_window, height=10, width=50)
        listbox.pack(pady=20)

        # Populate the listbox with registered users
        for user in self.user_secrets.keys():
            listbox.insert(tk.END, user)

        def delete_account():
            selected_user = listbox.get(tk.ACTIVE)
            if selected_user:
                confirmation = messagebox.askyesno("Confirm", f"Are you sure you want to delete '{selected_user}'?")
                if confirmation:
                    # Remove user from secrets and faces
                    del self.user_secrets[selected_user]
                    self.save_user_secrets()
                    # Remove face image
                    face_image_path = os.path.join(KNOWN_FACES_DIR, f"{selected_user}.jpg")
                    if os.path.exists(face_image_path):
                        os.remove(face_image_path)
                    listbox.delete(tk.ACTIVE)  # Remove from listbox

        def show_qr_code():
            selected_user = listbox.get(tk.ACTIVE)
            if selected_user:
                secret = self.user_secrets[selected_user]
                self.generate_qr_code(selected_user, secret)

        delete_button = tk.Button(admin_window, text="Delete Account", command=delete_account)
        delete_button.pack(pady=10)

        qr_button = tk.Button(admin_window, text="Show QR Code", command=show_qr_code)
        qr_button.pack(pady=10)

# Main Program
root = tk.Tk()
app = FaceRecognitionApp(root)
root.mainloop()