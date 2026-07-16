import time
import sys
import os

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
import models, schemas, vault, crypto

def run_benchmark():
    print("🚀 Initializing vault performance benchmark...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Setup Test User
    test_user = db.query(models.User).filter(models.User.username == "perf_tester").first()
    if not test_user:
        test_user = models.User(username="perf_tester", email="perf@tester.com", hashed_password="fake")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

    master_pwd = "MasterPassword123!"
    num_credentials = 50

    # Clean up any leftover credentials from previous interrupted runs
    db.query(models.Credential).filter(models.Credential.user_id == test_user.id).delete()
    db.commit()

    print(f"⏳ Generating and encrypting {num_credentials} credentials in a cache context...")
    start_create = time.time()
    
    with crypto.key_cache_context():
        for i in range(num_credentials):
            cred_data = schemas.CredentialCreate(
                service_name=f"Service-{i}",
                username=f"user-{i}@test.com",
                password=f"SecretPassword-{i}!",
                url=f"https://service-{i}.com",
                notes=f"Notes for service {i}",
                master_password=master_pwd
            )
            vault.VaultManager.create_credential(db, cred_data, test_user.id, master_pwd)
        
    end_create = time.time()
    create_duration = end_create - start_create
    print(f"✅ Encryption/Creation of {num_credentials} credentials completed in: {create_duration:.4f} seconds.")

    print(f"⏳ Fetching and decrypting all {num_credentials} credentials in a cache context...")
    start_decrypt = time.time()
    
    with crypto.key_cache_context():
        decrypted_creds = vault.VaultManager.get_credentials(db, test_user.id, master_pwd)
    
    end_decrypt = time.time()
    decrypt_duration = end_decrypt - start_decrypt
    print(f"✅ Decryption/Retrieval of {len(decrypted_creds)} credentials completed in: {decrypt_duration:.4f} seconds.")

    total_duration = create_duration + decrypt_duration
    print(f"✨ Total benchmark duration: {total_duration:.4f} seconds.")

    # 2. Cleanup
    print("🧹 Cleaning up benchmark data...")
    db.query(models.Credential).filter(models.Credential.user_id == test_user.id).delete()
    db.delete(test_user)
    db.commit()
    db.close()

    # Assert performance requirement (well under 2 seconds)
    assert total_duration < 2.0, f"Benchmark failed: took {total_duration:.4f} seconds, which is >= 2.0 seconds."
    print("🎉 BENCHMARK PASSED!")

if __name__ == "__main__":
    run_benchmark()
