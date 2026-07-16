from database import SessionLocal, engine, Base
import models, schemas, vault
import os

def test_vault_module():
    print("🚀 Initializing Vault Module Backend Test...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Setup Dummy User if necessary
    test_user = db.query(models.User).filter(models.User.username == "vault_tester").first()
    if not test_user:
        test_user = models.User(username="vault_tester", email="vault@tester.com", hashed_password="fake")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

    master_pwd = "MasterPassword123!"
    
    # 2. Create Credential
    print("🔹 Testing Credential Creation (Encrypted)...")
    new_cred_data = schemas.CredentialCreate(
        service_name="Google",
        username="tester@gmail.com",
        password="VerySecretPassword!",
        url="https://google.com",
        notes="Work account",
        master_password=master_pwd
    )
    
    created_cred = vault.VaultManager.create_credential(db, new_cred_data, test_user.id, master_pwd)
    print(f"✅ Created ID: {created_cred.id}")
    
    # 3. Check DB Store (Should be unreadable)
    print(f"🔐 Verifying Encryption in DB for ID {created_cred.id}...")
    db_record = db.query(models.Credential).filter(models.Credential.id == created_cred.id).first()
    print(f"   [DB] Encrypted Service: {db_record.service_name[:20]}...")
    assert db_record.service_name != "Google"

    # 4. Fetch and Decrypt
    print("🔓 Testing Decryption and Retrieval...")
    all_creds = vault.VaultManager.get_credentials(db, test_user.id, master_pwd)
    found = next(c for c in all_creds if c['id'] == created_cred.id)
    print(f"   [APP] Decrypted Service: {found['service_name']}")
    assert found['service_name'] == "Google"
    assert found['password'] == "VerySecretPassword!"

    # 5. Cleanup
    print("🧹 Cleaning up test data...")
    vault.VaultManager.delete_credential(db, created_cred.id, test_user.id)
    db.delete(test_user)
    db.commit()
    db.close()
    
    print("\n✨ STAGE 10 BACKEND TEST PASSED! ✨")

if __name__ == "__main__":
    test_vault_module()
