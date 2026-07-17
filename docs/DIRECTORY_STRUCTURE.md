# Directory Structure — PixelVault

```
PixelVault/                          ← Project root
│
├── backend/                         ← Python/FastAPI application
│   ├── main.py                      ← App entry point, all endpoints, middleware
│   ├── auth.py                      ← JWT + bcrypt authentication
│   ├── crypto.py                    ← AES-256-GCM encryption, PBKDF2 key derivation
│   ├── database.py                  ← SQLAlchemy engine, session factory
│   ├── models.py                    ← ORM table definitions
│   ├── schemas.py                   ← Pydantic request/response models + validation
│   ├── vault.py                     ← VaultManager: credential CRUD + health scoring
│   ├── audit.py                     ← AuditEngine: password strength + reuse detection
│   ├── secure_notes.py              ← NotesManager: encrypted note CRUD
│   ├── stego.py                     ← Image LSB steganography (PNG)
│   ├── audio_stego.py               ← Audio LSB steganography (WAV)
│   ├── video_stego.py               ← Video frame LSB steganography (AVI/FFV1)
│   ├── generator.py                 ← PasswordGenerator: random + smart passwords
│   ├── benchmark_vault.py           ← Performance benchmarking script (not imported)
│   ├── pixelvault.db                ← SQLite database (active — used by backend)
│   ├── uploads/                     ← Temporary stego output files
│   ├── test_stage10.py              ← Acceptance tests: vault encryption
│   ├── test_stage11.py              ← Acceptance tests: secure notes
│   ├── test_stage12.py              ← Acceptance tests: (verify specific stage)
│   ├── test_stage13.py              ← Acceptance tests: password generator + audit
│   ├── test_stego_roundtrip.py      ← Integration tests: stego embed/extract roundtrip
│   └── __pycache__/                 ← Python bytecode cache (ignore)
│
├── frontend/                        ← Static HTML/CSS/JS pages
│   ├── session-manager.js           ← SessionStorage wrapper (token, username, key)
│   ├── crypto-service.js            ← Web Crypto API PBKDF2 (future client-side use)
│   ├── api.js                       ← Centralized fetch client with auth headers
│   ├── auth-service.js              ← Login, register, logout, route guard
│   ├── index.html                   ← Login / registration page
│   ├── dashboard.html               ← Navigation hub
│   ├── vault.html                   ← Password vault UI
│   ├── notes.html                   ← Secure notes UI
│   ├── audit.html                   ← Security audit report UI
│   ├── stego.html                   ← Steganography embed/extract UI
│   └── generator.html               ← Client-side password generator UI
│
├── docs/                            ← AI Knowledge Base (this directory)
│   ├── AI_AGENT_PROTOCOL.md         ← Rules for future AI sessions
│   ├── PROJECT_MANIFEST.md          ← Project overview and tech stack
│   ├── ARCHITECTURE.md              ← System architecture deep-dive
│   ├── DIRECTORY_STRUCTURE.md       ← This file
│   ├── COMPONENT_INDEX.md           ← Feature-to-file mapping
│   ├── API_REFERENCE.md             ← All endpoint documentation
│   ├── DATABASE_SCHEMA.md           ← DB table and relationship docs
│   ├── AUTHENTICATION.md            ← Auth flow documentation
│   ├── CRYPTOGRAPHY.md              ← Encryption/decryption documentation
│   ├── STEGANOGRAPHY.md             ← Stego algorithm documentation
│   ├── DESIGN_SYSTEM.md             ← UI design system reference
│   ├── BACKEND_MODULES.md           ← Backend module reference
│   ├── FRONTEND_MODULES.md          ← Frontend module reference
│   ├── DEPENDENCY_GRAPH.md          ← Module dependency map
│   ├── KNOWN_BUGS.md                ← Known issues tracker
│   ├── TECHNICAL_DEBT.md            ← Technical debt registry
│   ├── CHANGELOG.md                 ← Version history
│   ├── WORK_LOG.md                  ← Session activity log
│   ├── TODO.md                      ← Prioritized roadmap
│   └── RELEASE_REPORT.md            ← Release report template
│
├── uploads/                         ← Root-level uploads dir (may be unused)
├── pixelvault.db                    ← Root-level DB (likely stale artifact)
├── requirements.txt                 ← Python package dependencies
├── .env.example                     ← Environment variable template
├── .gitignore                       ← Git exclusions
├── README.md                        ← Project overview
├── RUNNING.md                       ← How to start the application
└── PROJECT_REPORT.md                ← Academic/submission report
```

---

## Notes

- **Active database:** `backend/pixelvault.db` — this is what the running backend uses.
- **Root `pixelvault.db`:** Stale artifact. Can be deleted safely if confirmed unused.
- **`uploads/` (backend):** Contains temporary files generated during stego operations. Files are cleaned up after each request except the saved output files for history download. This directory should be regularly purged in production.
- **`venv/`:** Python virtual environment. Never read or modify.
- **`__pycache__/`:** Python bytecode. Never read or modify.
- **Test files** (`test_stage*.py`): Not imported by `main.py`. Run independently with `pytest`.
