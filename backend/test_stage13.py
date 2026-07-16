"""
test_stage13.py — Acceptance test: per-credential health_score and is_reused
are computed and stored after get_credentials(), not left as DB defaults.

Scenario:
  - One strong, unique password       → high score, not reused
  - One weak password                 → low score, not reused
  - Two credentials sharing the same password → medium score, both flagged reused
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
import models, schemas, vault
from audit import AuditEngine


def test_health_score_and_reuse():
    print("🚀 Initializing Stage 13: health_score / is_reused persistence test...\n")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # --- setup user ---
    test_user = db.query(models.User).filter(models.User.username == "score_tester").first()
    if not test_user:
        test_user = models.User(username="score_tester", email="score@tester.com", hashed_password="fake")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

    master_pwd = "MasterPassword123!"

    # Clean up any previous run
    db.query(models.Credential).filter(models.Credential.user_id == test_user.id).delete()
    db.commit()

    STRONG_PWD  = "V3ryStr0ng!Unique#Pwd"   # score 100
    WEAK_PWD    = "abc"                      # score 0
    REUSED_PWD  = "SharedPass1!"            # used twice

    def make(service, password):
        return schemas.CredentialCreate(
            service_name=service,
            username=f"{service}@test.com",
            password=password,
            master_password=master_pwd
        )

    print("🔹 Creating credentials...")
    vault.VaultManager.create_credential(db, make("StrongSite",   STRONG_PWD), test_user.id, master_pwd)
    vault.VaultManager.create_credential(db, make("WeakSite",     WEAK_PWD),   test_user.id, master_pwd)
    vault.VaultManager.create_credential(db, make("ReusedSiteA",  REUSED_PWD), test_user.id, master_pwd)
    vault.VaultManager.create_credential(db, make("ReusedSiteB",  REUSED_PWD), test_user.id, master_pwd)

    # --- call get_credentials to trigger full recompute ---
    print("🔹 Calling get_credentials (triggers _recompute_scores)...")
    creds = vault.VaultManager.get_credentials(db, test_user.id, master_pwd)

    by_service = {c["service_name"]: c for c in creds}

    expected_strong_score  = AuditEngine.check_strength(STRONG_PWD)
    expected_weak_score    = AuditEngine.check_strength(WEAK_PWD)
    expected_reused_score  = AuditEngine.check_strength(REUSED_PWD)

    # 1. Strong credential
    sc = by_service["StrongSite"]
    print(f"  StrongSite  → health_score={sc['health_score']}  is_reused={sc['is_reused']}")
    assert sc["health_score"] == expected_strong_score, (
        f"StrongSite score mismatch: got {sc['health_score']}, expected {expected_strong_score}")
    assert sc["is_reused"] is False, "StrongSite should not be reused"

    # 2. Weak credential
    wc = by_service["WeakSite"]
    print(f"  WeakSite    → health_score={wc['health_score']}  is_reused={wc['is_reused']}")
    assert wc["health_score"] == expected_weak_score, (
        f"WeakSite score mismatch: got {wc['health_score']}, expected {expected_weak_score}")
    assert wc["health_score"] < sc["health_score"], "Weak password should score lower than strong"
    assert wc["is_reused"] is False, "WeakSite should not be reused"

    # 3. Reused credentials
    ra = by_service["ReusedSiteA"]
    rb = by_service["ReusedSiteB"]
    print(f"  ReusedSiteA → health_score={ra['health_score']}  is_reused={ra['is_reused']}")
    print(f"  ReusedSiteB → health_score={rb['health_score']}  is_reused={rb['is_reused']}")
    assert ra["health_score"] == expected_reused_score
    assert rb["health_score"] == expected_reused_score
    assert ra["is_reused"] is True,  "ReusedSiteA should be flagged reused"
    assert rb["is_reused"] is True,  "ReusedSiteB should be flagged reused"

    # 4. Confirm DB rows were actually persisted (not just in-memory dicts)
    print("🔹 Verifying DB persistence...")
    raw_rows = db.query(models.Credential).filter(models.Credential.user_id == test_user.id).all()
    by_id = {r.id: r for r in raw_rows}

    ra_orm = by_id[ra["id"]]
    rb_orm = by_id[rb["id"]]
    sc_orm = by_id[sc["id"]]
    wc_orm = by_id[wc["id"]]

    assert sc_orm.health_score == expected_strong_score,  "DB: StrongSite score not persisted"
    assert wc_orm.health_score == expected_weak_score,    "DB: WeakSite score not persisted"
    assert ra_orm.is_reused is True,                      "DB: ReusedSiteA is_reused not persisted"
    assert rb_orm.is_reused is True,                      "DB: ReusedSiteB is_reused not persisted"
    assert sc_orm.is_reused is False,                     "DB: StrongSite wrongly marked reused"

    print("\n✅ All DB rows match computed values.")

    # --- cleanup ---
    print("🧹 Cleaning up...")
    db.query(models.Credential).filter(models.Credential.user_id == test_user.id).delete()
    db.delete(test_user)
    db.commit()
    db.close()

    print("\n✨ STAGE 13 TEST PASSED! ✨")


if __name__ == "__main__":
    test_health_score_and_reuse()
