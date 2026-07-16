import models, schemas, crypto
from sqlalchemy.orm import Session
from typing import List, Optional
import html
import io
import csv
from audit import AuditEngine

class VaultManager:
    """
    Handles core Password Manager operations including encryption-at-rest.
    All sensitive fields are encrypted before database storage.
    """

    @staticmethod
    def sanitize_data(data: str) -> str:
        """Prevent XSS by escaping HTML tags in user input."""
        return html.escape(data) if data else data

    @staticmethod
    def encrypt_vault_item(data: str, master_password: str) -> str:
        """Helper to encrypt a single field for the vault."""
        return crypto.encrypt_message(data, master_password)

    @staticmethod
    def decrypt_vault_item(encrypted_data: str, master_password: str) -> str:
        """Helper to decrypt a single field from the vault."""
        return crypto.decrypt_message(encrypted_data, master_password)

    @staticmethod
    def _recompute_scores(db: Session, db_creds: list, decrypted_list: list) -> None:
        """
        Recompute health_score and is_reused for every credential in the set
        using AuditEngine's existing formulas, then persist changes to the DB.

        db_creds      – list of models.Credential ORM objects (same order as decrypted_list)
        decrypted_list – list of dicts already built by get_credentials / create_credential;
                         mutated in-place so callers get live values without a re-decrypt.
        """
        if not decrypted_list:
            return

        # --- per-credential strength ---
        scores = {d["id"]: AuditEngine.check_strength(d["password"]) for d in decrypted_list}

        # --- cross-set reuse detection ---
        password_counts: dict = {}
        for d in decrypted_list:
            password_counts[d["password"]] = password_counts.get(d["password"], 0) + 1
        reused_ids = {d["id"] for d in decrypted_list if password_counts[d["password"]] > 1}

        # --- persist to DB rows & update the in-memory dicts ---
        id_to_orm = {c.id: c for c in db_creds}
        dirty = False
        for d in decrypted_list:
            cid = d["id"]
            new_score = scores[cid]
            new_reused = cid in reused_ids
            orm = id_to_orm.get(cid)
            if orm is not None and (orm.health_score != new_score or orm.is_reused != new_reused):
                orm.health_score = new_score
                orm.is_reused = new_reused
                dirty = True
            # Always update the returned dict so callers see the live value
            d["health_score"] = new_score
            d["is_reused"] = new_reused

        if dirty:
            db.commit()

    @staticmethod
    def create_credential(db: Session, cred: schemas.CredentialCreate, user_id: int, master_password: str):
        """Encrypt and store a new credential with prior sanitization."""
        with crypto.key_cache_context():
            new_cred = models.Credential(
                service_name=VaultManager.encrypt_vault_item(VaultManager.sanitize_data(cred.service_name), master_password),
                username=VaultManager.encrypt_vault_item(VaultManager.sanitize_data(cred.username), master_password),
                password=VaultManager.encrypt_vault_item(cred.password, master_password), # Don't escape passwords
                url=VaultManager.encrypt_vault_item(cred.url, master_password) if cred.url else None,
                totp_secret=VaultManager.encrypt_vault_item(cred.totp_secret, master_password) if cred.totp_secret else None,
                notes=VaultManager.encrypt_vault_item(VaultManager.sanitize_data(cred.notes), master_password) if cred.notes else None,
                user_id=user_id
            )
            db.add(new_cred)
            db.commit()
            db.refresh(new_cred)

            # Compute strength for this credential immediately (reuse resolved on next list call)
            new_cred.health_score = AuditEngine.check_strength(cred.password)
            db.commit()

            return new_cred

    @staticmethod
    def get_credentials(db: Session, user_id: int, master_password: str) -> List[dict]:
        """Fetch, decrypt and score all credentials for a user."""
        with crypto.key_cache_context():
            db_creds = db.query(models.Credential).filter(models.Credential.user_id == user_id).all()
            decrypted_list = []
            for c in db_creds:
                decrypted_list.append({
                    "id": c.id,
                    "service_name": VaultManager.decrypt_vault_item(c.service_name, master_password),
                    "username": VaultManager.decrypt_vault_item(c.username, master_password),
                    "password": VaultManager.decrypt_vault_item(c.password, master_password),
                    "url": VaultManager.decrypt_vault_item(c.url, master_password) if c.url else None,
                    "totp_secret": VaultManager.decrypt_vault_item(c.totp_secret, master_password) if c.totp_secret else None,
                    "notes": VaultManager.decrypt_vault_item(c.notes, master_password) if c.notes else None,
                    "health_score": c.health_score,
                    "is_reused": c.is_reused,
                    "created_at": c.created_at,
                    "updated_at": c.updated_at
                })

            # Recompute scores across the full set (handles reuse correctly)
            VaultManager._recompute_scores(db, db_creds, decrypted_list)

            return decrypted_list

    @staticmethod
    def delete_credential(db: Session, cred_id: int, user_id: int):
        """Remove a credential from the vault."""
        db_cred = db.query(models.Credential).filter(
            models.Credential.id == cred_id, 
            models.Credential.user_id == user_id
        ).first()
        if db_cred:
            db.delete(db_cred)
            db.commit()
            return True
        return False

    @staticmethod
    def generate_csv_export(credentials: List[dict]) -> str:
        """Format decrypted credentials into a CSV string."""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["service_name", "username", "password", "url", "notes"])
        writer.writeheader()
        for c in credentials:
            writer.writerow({
                "service_name": c["service_name"],
                "username": c["username"],
                "password": c["password"],
                "url": c["url"] or "",
                "notes": c["notes"] or ""
            })
        return output.getvalue()
