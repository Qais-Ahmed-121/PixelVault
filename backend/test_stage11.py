from database import SessionLocal, engine, Base
import models, schemas, secure_notes
import os

def test_notes_module():
    print("🚀 Initializing Secure Notes Backend Test...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Setup Dummy User
    test_user = db.query(models.User).filter(models.User.username == "notes_tester").first()
    if not test_user:
        test_user = models.User(username="notes_tester", email="notes@tester.com", hashed_password="fake")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

    master_pwd = "SafeMasterKey99!"
    
    # 2. Create Note
    print("🔹 Testing Note Creation (Encrypted)...")
    note_data = schemas.SecureNoteCreate(
        title="Server API Keys",
        content="SK_LIVE_1234567890abcdef",
        master_password=master_pwd
    )
    
    created_note = secure_notes.NotesManager.create_note(db, note_data, test_user.id, master_pwd)
    print(f"✅ Created Note ID: {created_note.id}")
    
    # 3. Check DB Store
    print(f"🔐 Verifying Encryption in DB for Note ID {created_note.id}...")
    db_record = db.query(models.SecureNote).filter(models.SecureNote.id == created_note.id).first()
    print(f"   [DB] Encrypted Title: {db_record.title[:20]}...")
    assert db_record.title != "Server API Keys"

    # 4. Fetch and Decrypt
    print("🔓 Testing Decryption and Retrieval...")
    all_notes = secure_notes.NotesManager.get_notes(db, test_user.id, master_pwd)
    found = next(n for n in all_notes if n['id'] == created_note.id)
    print(f"   [APP] Decrypted Title: {found['title']}")
    assert found['title'] == "Server API Keys"
    assert found['content'] == "SK_LIVE_1234567890abcdef"

    # 5. Cleanup
    print("🧹 Cleaning up test data...")
    secure_notes.NotesManager.delete_note(db, created_note.id, test_user.id)
    db.delete(test_user)
    db.commit()
    db.close()
    
    print("\n✨ STAGE 11 BACKEND TEST PASSED! ✨")

if __name__ == "__main__":
    test_notes_module()
