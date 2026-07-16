import models, schemas, crypto
from sqlalchemy.orm import Session
from typing import List
import html

class NotesManager:
    """
    Handles encrypted storage and retrieval of secure notes.
    Uses the user's master password for field-level AES-256-GCM encryption.
    """

    @staticmethod
    def sanitize(data: str) -> str:
        return html.escape(data) if data else data

    @staticmethod
    def create_note(db: Session, note: schemas.SecureNoteCreate, user_id: int, master_password: str):
        """Encrypt and save a new secure note with sanitization."""
        with crypto.key_cache_context():
            encrypted_title = crypto.encrypt_message(NotesManager.sanitize(note.title), master_password)
            encrypted_content = crypto.encrypt_message(NotesManager.sanitize(note.content), master_password)
            
            db_note = models.SecureNote(
                title=encrypted_title,
                content=encrypted_content,
                user_id=user_id
            )
            db.add(db_note)
            db.commit()
            db.refresh(db_note)
            return db_note

    @staticmethod
    def get_notes(db: Session, user_id: int, master_password: str) -> List[dict]:
        """Retrieve and decrypt all secure notes for a user."""
        with crypto.key_cache_context():
            db_notes = db.query(models.SecureNote).filter(models.SecureNote.user_id == user_id).all()
            decrypted_notes = []
            
            for n in db_notes:
                try:
                    decrypted_notes.append({
                        "id": n.id,
                        "title": crypto.decrypt_message(n.title, master_password),
                        "content": crypto.decrypt_message(n.content, master_password),
                        "created_at": n.created_at,
                        "updated_at": n.updated_at
                    })
                except Exception:
                    # Handle cases where decryption might fail due to wrong password or corruption
                    continue
                    
            return decrypted_notes

    @staticmethod
    def delete_note(db: Session, note_id: int, user_id: int):
        """Securely delete a note."""
        db_note = db.query(models.SecureNote).filter(
            models.SecureNote.id == note_id,
            models.SecureNote.user_id == user_id
        ).first()
        if db_note:
            db.delete(db_note)
            db.commit()
            return True
        return False
