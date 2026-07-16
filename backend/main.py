from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
import uvicorn
import os
import uuid
from database import engine, Base, get_db
import models, schemas, auth, crypto, stego, audio_stego, video_stego, vault, audit, secure_notes
from datetime import timedelta
from typing import List
import html

# Security Constants
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".wav", ".mp4", ".avi"}

# Ensure uploads directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StegaVault API",
    description="Advanced Secure Steganography Web Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# --- Helper Functions ---

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS/Injection."""
    return html.escape(text.strip())

async def validate_file(file: UploadFile):
    """
    Harden file validation: 
    1. Check if file object exists
    2. Validate extension
    3. Check file size before heavy processing
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format" # Secure error: don't list allowed types unless necessary
        )
    
    # Check size early
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0) # Reset pointer
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds 5MB limit")
        
    return True

# --- Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "StegaVault API is running",
        "version": "1.0.0"
    }

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with secure password hashing."""
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token login, returns a JWT."""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """Retrieve the current authenticated user profile."""
    return current_user

@app.post("/embed/image")
@app.post("/stego/hide")
async def embed_image(
    file: UploadFile = File(...),
    message: str = Form(...),
    password: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Encrypt and hide a message in an image."""
    await validate_file(file)
    message = message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    encrypted_msg = crypto.encrypt_message(message, password)

    output_filename = f"stego_{uuid.uuid4()}.png"
    output_path = os.path.join(UPLOAD_DIR, output_filename)
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{uuid.uuid4()}.png")

    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        stego.hide_message(temp_path, encrypted_msg, output_path)
    except Exception as e:
        print(f"[SECURITY] Image Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to process image")
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

    media_file = models.MediaFile(filename=output_filename, filepath=output_path, file_type="png", owner_id=current_user.id)
    db.add(media_file); db.commit(); db.refresh(media_file)
    
    operation = models.StegoOperation(
        operation_type="hide_image",
        description=f"Hid message in {file.filename} (Image)",
        user_id=current_user.id,
        media_file_id=media_file.id
    )
    db.add(operation); db.commit()
    return FileResponse(output_path, media_type="image/png", filename="stegavault_result.png")

@app.post("/embed/audio")
async def embed_audio(
    file: UploadFile = File(...),
    message: str = Form(...),
    password: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Encrypt and hide a message in a WAV audio file."""
    await validate_file(file)
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Invalid audio format")
    
    message = message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    encrypted_msg = crypto.encrypt_message(message, password)

    output_filename = f"audio_stego_{uuid.uuid4()}.wav"
    output_path = os.path.join(UPLOAD_DIR, output_filename)
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{uuid.uuid4()}.wav")

    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        audio_stego.hide_message(temp_path, encrypted_msg, output_path)
    except Exception as e:
        print(f"[SECURITY] Audio Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to process audio")
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

    media_file = models.MediaFile(filename=output_filename, filepath=output_path, file_type="wav", owner_id=current_user.id)
    db.add(media_file); db.commit(); db.refresh(media_file)
    
    operation = models.StegoOperation(
        operation_type="hide_audio",
        description=f"Hid message in {file.filename} (Audio)",
        user_id=current_user.id, media_file_id=media_file.id
    )
    db.add(operation); db.commit()

    return FileResponse(output_path, media_type="audio/wav", filename="stegavault_audio.wav")

@app.post("/embed/video")
async def embed_video(
    file: UploadFile = File(...),
    message: str = Form(...),
    password: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Encrypt and hide a message in a Video file (MP4/AVI)."""
    await validate_file(file)
    if not (file.filename.lower().endswith(".mp4") or file.filename.lower().endswith(".avi")):
        raise HTTPException(status_code=400, detail="Invalid video format")
    
    message = message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    encrypted_msg = crypto.encrypt_message(message, password)

    output_filename = f"video_stego_{uuid.uuid4()}.avi"
    output_path = os.path.join(UPLOAD_DIR, output_filename)
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{uuid.uuid4()}.avi")

    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        video_stego.hide_message(temp_path, encrypted_msg, output_path)
    except Exception as e:
        print(f"[SECURITY] Video Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to process video")
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

    media_file = models.MediaFile(filename=output_filename, filepath=output_path, file_type="video", owner_id=current_user.id)
    db.add(media_file); db.commit(); db.refresh(media_file)
    
    operation = models.StegoOperation(
        operation_type="hide_video",
        description=f"Hid message in {file.filename} (Video)",
        user_id=current_user.id, media_file_id=media_file.id
    )
    db.add(operation); db.commit()

    return FileResponse(output_path, media_type="video/x-msvideo", filename="stegavault_video.avi")

@app.get("/stego/download/{media_file_id}")
def download_stego_image(
    media_file_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve and download a previously processed stego-image."""
    media_file = db.query(models.MediaFile).filter(
        models.MediaFile.id == media_file_id,
        models.MediaFile.owner_id == current_user.id
    ).first()
    
    if not media_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not os.path.exists(media_file.filepath):
        raise HTTPException(status_code=404, detail="File no longer exists on server")
    
    return FileResponse(media_file.filepath, media_type="image/png", filename="stegavault_download.png")

@app.post("/extract/image")
@app.post("/stego/extract", response_model=schemas.ExtractionResult)
async def stego_extract(
    file: UploadFile = File(...),
    password: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Extract and decrypt a message from an image."""
    await validate_file(file)
    temp_path = os.path.join(UPLOAD_DIR, f"extract_{uuid.uuid4()}.png")
    
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        encrypted_payload = stego.extract_message(temp_path)
        decrypted_msg = crypto.decrypt_message(encrypted_payload, password)
        
        operation = models.StegoOperation(
            operation_type="extract_image",
            description=f"Extracted from {file.filename} (Image)",
            user_id=current_user.id
        )
        db.add(operation); db.commit()
        return {"message": decrypted_msg}
    except Exception as e:
        print(f"[SECURITY] Image Extraction Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Extraction failed")
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@app.post("/extract/audio")
async def extract_audio(
    file: UploadFile = File(...),
    password: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Extract and decrypt a message from a WAV audio file."""
    await validate_file(file)
    temp_path = os.path.join(UPLOAD_DIR, f"extract_{uuid.uuid4()}.wav")
    
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        encrypted_payload = audio_stego.extract_message(temp_path)
        decrypted_msg = crypto.decrypt_message(encrypted_payload, password)
        
        operation = models.StegoOperation(
            operation_type="extract_audio",
            description=f"Extracted from {file.filename} (Audio)",
            user_id=current_user.id
        )
        db.add(operation); db.commit()
        return {"message": decrypted_msg}
    except Exception as e:
        print(f"[SECURITY] Audio Extraction Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Extraction failed")
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@app.post("/extract/video")
async def extract_video(
    file: UploadFile = File(...),
    password: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Extract and decrypt a message from a Video file."""
    await validate_file(file)
    temp_path = os.path.join(UPLOAD_DIR, f"extract_{uuid.uuid4()}.avi") # We mainly extract from avi output
    
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        encrypted_payload = video_stego.extract_message(temp_path)
        decrypted_msg = crypto.decrypt_message(encrypted_payload, password)
        
        operation = models.StegoOperation(
            operation_type="extract_video",
            description=f"Extracted from {file.filename} (Video)",
            user_id=current_user.id
        )
        db.add(operation); db.commit()
        return {"message": decrypted_msg}
    except Exception as e:
        print(f"[SECURITY] Video Extraction Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Extraction failed")
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@app.get("/stego/history", response_model=List[schemas.StegoHistoryOut])
def get_stego_history(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Retrieve the operation history for the current user."""
    return db.query(models.StegoOperation).filter(models.StegoOperation.user_id == current_user.id).all()

# --- Vault API Endpoints ---

@app.post("/vault/add", response_model=schemas.CredentialOut)
async def add_vault_credential(
    req: schemas.CredentialCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Encrypt and store a new credential in the vault."""
    try:
        new_cred = vault.VaultManager.create_credential(db, req, current_user.id, req.master_password)
        return new_cred
    except Exception as e:
        print(f"[ERROR] Vault Add: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to add credential")

@app.post("/vault/list", response_model=List[dict])
async def list_vault_credentials(
    req: schemas.VaultListRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Decrypt and list all credentials for the current user."""
    try:
        return vault.VaultManager.get_credentials(db, current_user.id, req.master_password)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid master password")

@app.delete("/vault/delete/{cred_id}")
async def delete_vault_credential(
    cred_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a credential from the vault."""
    success = vault.VaultManager.delete_credential(db, cred_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Credential not found")
    return {"message": "Credential deleted successfully"}

@app.post("/vault/audit")
async def audit_vault(
    req: schemas.VaultListRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Perform a security audit on all vault passwords."""
    try:
        credentials = vault.VaultManager.get_credentials(db, current_user.id, req.master_password)
        return audit.AuditEngine.analyze_vault(credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Audit failed. Verify master password.")

@app.post("/vault/export")
async def export_vault(
    req: schemas.VaultListRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Securely export vault credentials as a CSV file."""
    try:
        credentials = vault.VaultManager.get_credentials(db, current_user.id, req.master_password)
        csv_content = vault.VaultManager.generate_csv_export(credentials)
        
        headers = {
            'Content-Disposition': 'attachment; filename="stegavault_backup.csv"'
        }
        return Response(content=csv_content, media_type="text/csv", headers=headers)
    except Exception:
        raise HTTPException(status_code=401, detail="Export failed. Verify master password.")

# --- Secure Notes API Endpoints ---

@app.post("/notes/add", response_model=schemas.SecureNoteOut)
async def add_secure_note(
    req: schemas.SecureNoteCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Encrypt and store a new secure note."""
    try:
        return secure_notes.NotesManager.create_note(db, req, current_user.id, req.master_password)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to save note")

@app.post("/notes/list", response_model=List[dict])
async def list_secure_notes(
    req: schemas.NotesListRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Decrypt and list all secure notes for the user."""
    return secure_notes.NotesManager.get_notes(db, current_user.id, req.master_password)

@app.delete("/notes/delete/{note_id}")
async def delete_secure_note(
    note_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a secure note."""
    success = secure_notes.NotesManager.delete_note(db, note_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
