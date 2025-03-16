Here’s a professional and structured description of your face recognition authentication project:  

---

# Face-Recognition-OTP-Authentication  

## 🔐 About This Project  
Face-Recognition-OTP-Authentication is a secure multi-factor authentication system that combines **facial recognition** and **one-time password (OTP) verification**. This project ensures a **high level of security** by requiring both biometric authentication and a time-based OTP for user access.  

## ⚡ Features  
- **Face Recognition Login**: Uses OpenCV and Face_Recognition libraries for real-time face detection and authentication.  
- **Two-Factor Authentication (2FA)**: Generates and verifies time-sensitive OTPs using PyOTP.  
- **User Registration & Management**: Allows users to register, store their facial data, and retrieve OTP-based authentication.  
- **Admin Control Panel**: Provides administrative privileges for managing user data and authentication.  
- **QR Code Authentication Setup**: Users can scan a QR code to link their account with an authenticator app.  
- **Secure Data Handling**: User secrets are securely stored and managed for enhanced privacy protection.  
- **Real-Time Camera Feed**: Uses OpenCV to display live video frames during face recognition.  
- **Graphical User Interface (GUI)**: Built with Tkinter for an intuitive user experience.  

## 🛠️ Technologies Used  
- **Python**: The core language for backend processing.  
- **OpenCV**: Real-time image processing for face detection and recognition.  
- **Face_Recognition**: A deep learning-based library for encoding and matching faces.  
- **PyOTP**: Secure time-based OTP generation for two-factor authentication.  
- **QRCode**: Used for generating QR codes for secure OTP authentication.  
- **Tkinter**: GUI framework for creating the desktop application interface.  
- **Pillow**: Image processing library for handling QR codes and user images.  

## 🚀 How It Works  
1. **User Registration**:  
   - The user registers by providing a username.  
   - The system captures and stores their facial image.  
   - A unique OTP secret key is generated and linked to the user.  
   - A QR code is provided for setting up OTP in an authenticator app.  

2. **User Login**:  
   - The user enters their username.  
   - The system verifies their face in real time using the webcam.  
   - If face recognition is successful, the user enters a time-sensitive OTP from their authenticator app.  
   - Upon correct OTP verification, access is granted.  

3. **Admin Features**:  
   - Admins can manage user accounts (view, delete users).  
   - They can regenerate QR codes for users if needed.  

## 📂 Project Structure  
```
Face-Recognition-OTP-Authentication/  
│── known_faces/          # Stored facial images of registered users  
│── user_secrets.txt      # Stores OTP secret keys for users  
│── main.py               # Core application logic (GUI, authentication)  
│── requirements.txt      # Dependencies for the project  
│── README.md             # Project documentation  
```

## 📜 Installation & Usage  
### 🔧 Requirements  
- Python 3.x  
- OpenCV (`pip install opencv-python`)  
- Face_Recognition (`pip install face_recognition`)  
- PyOTP (`pip install pyotp`)  
- Pillow (`pip install pillow`)  
- QRCode (`pip install qrcode`)  

