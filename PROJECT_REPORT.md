# PixelVault: Project Presentation Report 🛡️✨

**Project Title:** PixelVault - Advanced Multi-Media Steganography & Secure Vault  
**Field:** Information Security / Cryptography  
**Developer:** [Your Name]

---

## 1. Project Overview
**PixelVault** is a "Privacy-First" web application designed to protect sensitive information using two powerful techniques:
1.  **Steganography:** Hiding secret data inside ordinary media files (Images, Audio, Video).
2.  **Cryptography:** Storing passwords and notes in a fully encrypted digital vault.

Unlike traditional lockers, PixelVault provides **deniability**. If someone sees an image, they don't know it contains a secret message.

---

## 2. The Core Pillars (Modules)

### 🔵 Module 1: Authentication & Identity
*   **Purpose:** Ensures only authorized users can access the system.
*   **Security:** Uses **JWT (JSON Web Tokens)** for session management and **Argon2/Bcrypt** for hashing passwords. Your password is never stored in plain text!

### 🟢 Module 2: Multi-Media Steganography Hub
This is the heart of the project. We support three types of carriers:
*   **Image Stego:** Uses the LSB (Least Significant Bit) technique in PNG/JPG.
*   **Audio Stego:** Hides data in WAV files by modifying bit patterns.
*   **Video Stego:** Embeds data across frames in MP4/AVI files.
*   *Key Feature:* All hidden messages are **First Encrypted** before being hidden.

### 🟣 Module 3: Encrypted Password Vault
*   **Purpose:** A secure place to store login credentials.
*   **Algorithm:** Uses **AES-256-GCM** (Industry Standard).
*   **Master Password:** Everything is locked behind one Master Password. If you don't have it, the data remains scrambled gibberish in the database.

### 🔴 Module 4: Security Audit Engine
*   **Purpose:** To tell the user how safe they are.
*   **Functions:** 
    *   Checks for **Weak Passwords** (length, complexity).
    *   Detects **Password Reuse** (using the same password for different sites).
    *   Calculates an overall **Vault Health Score**.

### 🟡 Module 5: Quantum-Inspired Generator
*   **Purpose:** Creating unhackable passwords.
*   **Modes:** 
    *   *Random:* High-entropy strings.
    *   *Smart Keyword:* Memorable passwords using "Leet-Speak" (e.g., "Secret" becomes "S3cr3t!").

---

## 3. Technical Architecture (How it Works)

### The Backend (The Brain)
*   **Language:** Python
*   **Framework:** FastAPI (High performance, modern).
*   **Database:** SQLite (Lightweight and portable).
*   **Security Logic:** Custom modules for LSB steganography and AES-256 field-level encryption.

### The Frontend (The Face)
*   **Technologies:** HTML5, Vanilla JavaScript, Tailwind CSS.
*   **Design:** "Nebula Glassmorphism" – a premium, modern dark-mode aesthetic with smooth animations and responsive cards.

---

## 4. Step-by-Step User Flow

1.  **Registration:** User creates an account with a secure password.
2.  **Dashboard:** User chooses between Steganography (Hiding data) or the Vault (Storing data).
3.  **Hiding Data:** User uploads an image -> Types a secret -> Downloads the "Stego-File."
4.  **Extracting Data:** User uploads the "Stego-File" -> Enters message password -> The secret is revealed.
5.  **Vault Access:** User enters "Master Password" -> Vault unlocks -> User manages credentials.

---

## 5. Security Measures (Viva Special)
*If the examiner asks about security, mention these:*
*   **Encryption at Rest:** Data in the database is unusable without the key.
*   **Sanitization:** All user inputs are cleaned to prevent XSS (Cross-Site Scripting).
*   **Zero Knowledge:** The system doesn't know your Master Password; it only uses it to decrypt things locally.
*   **LSB Protection:** Modifying the least significant bit ensures the media file looks and sounds exactly like the original.

---

## 6. Common Viva Questions & Answers

**Q: Why use Steganography over just Encryption?**  
*A: Encryption makes a message unreadable, but it attracts attention (people know it's a secret). Steganography hides the **existence** of the message entirely.*

**Q: What happens if I forget my Master Password?**  
*A: For security reasons, the data is lost. We do not store the Master Password, ensuring that even if the database is stolen, the hacker can't see anything.*

**Q: Why use Python for this?**  
*A: Python has powerful libraries like `cryptography` and `numpy` which make handling binary data (for steganography) very efficient.*

---

## 7. Conclusion
PixelVault represents a modern approach to Information Security. By combining the stealth of Steganography with the strength of AES-256 Encryption, it provides a dual-layer defense system that is both user-friendly and highly secure.

---
**Presented by:** [Your Name]  
**Class:** [Your Class/Semester]  
**Instructor:** [Instructor Name]
