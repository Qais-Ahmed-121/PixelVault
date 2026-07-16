from audit import AuditEngine

def test_audit_module():
    print("🚀 Initializing Security Audit Engine Test...")
    
    # 1. Setup Mock Credentials (Decrypted)
    mock_creds = [
        {
            "service_name": "Google",
            "password": "Weak" # Very weak
        },
        {
            "service_name": "Facebook",
            "password": "StrongPassword123!" # Strong
        },
        {
            "service_name": "Twitter",
            "password": "StrongPassword123!" # Reused
        }
    ]

    print("🔹 Running Audit Analysis...")
    report = AuditEngine.analyze_vault(mock_creds)
    
    print(f"📊 Overall Health Score: {report['health_score']}%")
    print(f"📈 Stats: {report['stats']}")
    
    # Verify Weak Password Detection
    weak_alerts = [a for a in report['alerts'] if a['type'] == 'WEAK_PASSWORD']
    print(f"⚠️ Weak Password Alerts: {len(weak_alerts)}")
    assert len(weak_alerts) > 0
    assert weak_alerts[0]['service'] == "Google"

    # Verify Reuse Detection
    reuse_alerts = [a for a in report['alerts'] if a['type'] == 'REUSED_PASSWORD']
    print(f"♻️ Reused Password Alerts: {len(reuse_alerts)}")
    assert len(reuse_alerts) == 2 # Both Facebook and Twitter reuse are flagged

    assert report['health_score'] < 100 # Should be penalized
    
    print("\n✨ STAGE 12 AUDIT ENGINE TEST PASSED! ✨")

if __name__ == "__main__":
    test_audit_module()
