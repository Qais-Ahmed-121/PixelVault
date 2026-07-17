# 🛡️ PixelVault – Advanced Multi-Media Steganography & Password Manager

PixelVault is a production-ready, security-hardened platform designed to protect your digital assets. It combines **Triple-Layer Multi-Media Steganography** with a **Zero-Knowledge Password Manager**.

## 🚀 Key Modules

### 1. 📬 Steganography Hub
Hide encrypted secrets within Images, Audio, and Video files using advanced LSB manipulation.
- **Image**: PNG/JPG support with lossless bit-shifting.
- **Audio**: WAV-based high-fidelity audio steganography.
- **Video**: FFV1-lossless video encoding to ensure data integrity.
- **Security**: AES-256-GCM encryption is applied *before* hiding.

### 2. 🔐 Zero-Knowledge Vault
A full-featured password manager that gives you total control.
- **Vault Dashboard**: Track total items and vault health.
- **Secure Notes**: Encrypted notepad for sensitive snippets/recovery keys.
- **Quantum Generator**: 
    - *Random Mode*: Cryptographically secure high-entropy keys.
    - *Smart Mode*: Memorable but secure leet-speak based keys.
- **Security Audit**: Real-time analysis for weak and reused passwords.
- **Secure Export**: One-click decrypted CSV backup (requires Master Password).

---

## 🛠️ Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite.
- **Security**: PyCryptodome (AES-256-GCM, PBKDF2), Passlib (Bcrypt).
- **Processing**: Pillow (Image), NumPy (Matrix Ops), OpenCV (Video).
- **Frontend**: Tailwind CSS, Vanilla JS, Nebula Dark Theme.

---

## 📥 Setup & Installation

### 1. Requirements
- Python 3.11+
- Virtual Environment (recommended)

### 2. Installation
```powershell
pip install -r requirements.txt
```

### 3. Running the App
For detailed, step-by-step instructions, please refer to [RUNNING.md](RUNNING.md).

Quick start:
```powershell
python backend/main.py
```
Open `frontend/index.html` in your browser.


---

## 🧠 Security Architecture
The platform operates on a **Zero-Knowledge Basis**:
1. **Master Password**: Your Master Password is used to derive a symmetric encryption key locally. It is never stored on the server.
2. **Encryption-at-Rest**: Credentials and Notes are stored in the database as AES-256-GCM encrypted blobs.
3. **Escaping & Validation**: All user inputs are sanitized (HTML escaping) to prevent XSS attacks.

---

## 🎓 Viva / Defense Notes

### Q: Why include a Password Manager in a Steganography project?
**A:** Multi-layered security. Users can store their sensitive keys in the Vault and then use those keys to embed messages into media files. It provides a complete "SecOps" ecosystem for the user.

### Q: How does the "Smart Generator" work?
**A:** It takes a memorable keyword (e.g., "Nebula"), applies a **Leet-Speak Transformation** (e.g., "N3buL@"), and then appends cryptographic random padding to reach the required security length. It balances usability with security.

### Q: What is the "Health Score"?
**A:** A weighted algorithm that averages individual password strengths and applies a **Reuse Penalty**. If a password is used across multiple services, the vault's score drops significantly, encouraging better security habits.

---

## 🔮 Future Scope
- **TOTP Integration**: Dedicated UI for 2FA token generation.
- **Cloud Sync**: Encrypted database syncing via secure API hooks.
- **Mobile PWA**: Enable mobile usage for on-the-go steganography.
