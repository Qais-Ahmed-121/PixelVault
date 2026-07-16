# 🏃 How to Run StegaVault

Follow these steps to get the **StegaVault** platform up and running on your local machine.

---

## 🛠️ Prerequisites
- **Python 3.11+**: Ensure you have Python installed. You can check by running `python --version`.
- **Pip**: Python package manager (usually comes with Python).

---

## 📥 Step 1: Installation

1. **(Optional) Create a Virtual Environment**:
   It is highly recommended to use a virtual environment to keep dependencies isolated.
   ```powershell
   python -m venv venv
   

   ```

2. **Install Dependencies**:
   Install all required Python libraries using the `requirements.txt` file.
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🚀 Step 2: Start the Backend Server

The backend is built with FastAPI. To start it, run the main entry point:

```powershell
python backend/main.py
```

- The server will start at: `http://127.0.0.1:8000`
- You can view the automated API documentation at: `http://127.0.0.1:8000/docs`

---

## 🌐 Step 3: Launch the Frontend

StegaVault's frontend is a modern web interface built with vanilla HTML/JS and Tailwind CSS.

1. Navigate to the `frontend` folder.
2. Open `index.html` in your favorite web browser (Chrome, Edge, or Firefox).
   - Alternatively, you can right-click `index.html` and select **"Open with..."**.

---

## 💡 Quick Start Guide

1. **Register/Login**: Start by creating an account on the landing page.
2. **Setup Vault**: Go to the **Vault** section and set a **Master Password**. This password is used to encrypt your credentials and notes locally.
3. **Hide Secrets**: 
   - Upload an Image, Audio, or Video file.
   - Enter your secret message and a password.
   - Download the generated "Stego" file.
4. **Extract Secrets**:
   - Upload the stego file you just created.
   - Enter the same password used during embedding.
   - Retrieve your hidden message!

---

## ⚠️ Troubleshooting

- **Port in Use**: If you see an error saying port `8000` is already in use, you can change the port in `backend/main.py` at the very bottom line.
- **Missing Dependencies**: Ensure you are in the correct directory and your virtual environment is activated before running `pip install`.
- **CORS Errors**: The backend is configured to allow all origins, so you should not face CORS issues when opening the HTML files locally.
