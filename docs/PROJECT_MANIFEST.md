# Project Manifest — PixelVault

## Purpose

PixelVault is a full-stack cybersecurity web application that combines three capabilities in a single authenticated platform:

1. **Multi-Media Steganography** — Hide and extract AES-256-GCM encrypted messages inside image (PNG), audio (WAV), and video (AVI/MP4) files using LSB embedding.
2. **Encrypted Password Vault** — Store and manage credentials encrypted at-rest using the user's master password. Includes health scoring and reuse detection.
3. **Secure Notes** — Store arbitrary encrypted text notes (keys, recovery codes, memos) using the same master-password-based encryption.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML5 + CSS + JavaScript (no framework) |
| Styling | Tailwind CSS (CDN) |
| Backend | Python 3.11+, FastAPI 0.104 |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (`pixelvault.db`) |
| Auth | JWT (HS256) via `python-jose`, bcrypt for password hashing |
| Crypto | PyCryptodome — AES-256-GCM + PBKDF2 |
| Image Stego | NumPy + Pillow — LSB in pixel array |
| Audio Stego | Python `wave` + NumPy — LSB in PCM frames |
| Video Stego | OpenCV + NumPy — LSB across video frames |
| Server | Uvicorn ASGI, port 8000 |

---

## Major Modules

### Backend (`/backend`)

| File | Responsibility |
|---|---|
| `main.py` | FastAPI app, all endpoints, CORS, rate limiting, file validation |
| `auth.py` | JWT creation/verification, bcrypt hashing, `get_current_user` dependency |
| `crypto.py` | AES-256-GCM encryption/decryption, PBKDF2 key derivation, context-var key cache |
| `models.py` | SQLAlchemy ORM models: User, MediaFile, StegoOperation, Credential, SecureNote |
| `schemas.py` | Pydantic request/response schemas, password complexity validation |
| `database.py` | SQLite engine, session factory, `get_db` dependency |
| `vault.py` | `VaultManager` — credential CRUD with field-level encryption and health scoring |
| `audit.py` | `AuditEngine` — password strength scoring (0–100), reuse detection, vault health |
| `secure_notes.py` | `NotesManager` — encrypted note CRUD |
| `stego.py` | Image LSB hide/extract (PNG) |
| `audio_stego.py` | Audio LSB hide/extract (WAV) |
| `video_stego.py` | Video frame LSB hide/extract (AVI, lossless FFV1 codec) |
| `generator.py` | `PasswordGenerator` — cryptographically secure random + smart keyword-based passwords |

### Frontend (`/frontend`)

| File | Responsibility |
|---|---|
| `session-manager.js` | Centralized `sessionStorage` wrapper: token, username, encryptionKey (= raw master password), sliding 30-min expiry |
| `crypto-service.js` | PBKDF2 key derivation via Web Crypto API (reserved for future client-side encryption) |
| `api.js` | Centralized fetch wrapper: auto-injects `Authorization: Bearer` header, handles 401 globally |
| `auth-service.js` | Login (FormData POST to `/login`), register (JSON POST to `/register`), logout, route guard (`checkAuth()`) |
| `index.html` | Login / registration page |
| `dashboard.html` | Navigation hub |
| `vault.html` | Password vault UI — list, add, delete, export credentials |
| `notes.html` | Secure notes UI — list, add, delete notes |
| `audit.html` | Security audit UI — health score ring, alert list |
| `stego.html` | Steganography UI — embed/extract for image/audio/video, operation history |
| `generator.html` | Client-side password generator UI (no backend calls) |

---

## Folder Organization

```
PixelVault/
├── backend/          # FastAPI application
├── frontend/         # Static HTML/JS/CSS pages
├── docs/             # AI Knowledge Base (this directory)
├── uploads/          # Temporary/processed stego files (server-side)
├── pixelvault.db     # Root-level SQLite (unused — see backend/pixelvault.db)
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variable template
└── README.md / RUNNING.md
```

> **Note:** Two `pixelvault.db` files exist — one at root and one in `/backend`. The backend uses `/backend/pixelvault.db`. The root-level file is likely a stale artifact.

---

## Security Architecture

1. **Transport:** HTTP (localhost dev). No HTTPS in current setup.
2. **Authentication:** JWT Bearer token, 30-minute expiry, HS256.
3. **Authorization:** All protected endpoints use `Depends(auth.get_current_user)`.
4. **Encryption at rest:** All vault credential fields and note content encrypted with AES-256-GCM using user's master password. The master password is never stored.
5. **Key derivation:** PBKDF2-SHA256, 1,000,000 iterations, random 16-byte salt per record (embedded in ciphertext).
6. **Password hashing:** bcrypt with auto-generated salt for user login passwords.
7. **Rate limiting:** In-memory per-user counters — 5 failures in 15 minutes triggers lockout.
8. **Input sanitization:** `html.escape()` applied to all text before encryption.
9. **Session storage:** Frontend uses `sessionStorage` (tab-scoped) — cleared on tab close.

---

## Application Flow

```
User opens index.html
  → auth-service.js checkAuth() runs
    → No session → stays on login page
    → Valid session → redirect to dashboard.html

User logs in (index.html)
  → AuthService.login(username, password)
    → POST /login → receives JWT
    → SessionManager.saveSession(token, username, raw_password)
    → Redirect to dashboard.html

User opens vault.html
  → auth-service.js checkAuth() → session valid, stays
  → DOMContentLoaded → SessionManager.getSession()
    → session.encryptionKey (raw master password) → loadVault()
    → POST /vault/audit + POST /vault/list → decrypt + render

User logs out (any page)
  → AuthService.logout()
    → SessionManager.clearSession()
    → Redirect to index.html
```
