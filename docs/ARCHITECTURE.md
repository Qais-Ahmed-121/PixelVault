# Architecture — PixelVault

---

## 1. Frontend Architecture

PixelVault's frontend is a **multi-page application (MPA)** built with static HTML files served directly by a file system or simple HTTP server. There is no build step, bundler, or frontend framework.

### Page Map

```
index.html          ← Login / Register (public)
dashboard.html      ← Hub / navigation (protected)
vault.html          ← Password Vault (protected)
notes.html          ← Secure Notes (protected)
audit.html          ← Security Audit (protected)
stego.html          ← Steganography (protected)
generator.html      ← Password Generator (protected)
```

### JavaScript Service Layer

All pages load four shared service scripts in this exact order (from `<head>`):

```html
<script src="session-manager.js"></script>   <!-- 1: Session state -->
<script src="crypto-service.js"></script>    <!-- 2: Key derivation (future use) -->
<script src="api.js"></script>               <!-- 3: Fetch wrapper -->
<script src="auth-service.js"></script>      <!-- 4: Auth guard (runs checkAuth on load) -->
```

`auth-service.js` automatically runs `checkAuth()` as the last script to execute, enforcing route protection before any page logic runs.

### Data Flow (Frontend)

```
Page Load
  → auth-service.js (checkAuth)
    → SessionManager.getSession()
      → Valid: page continues
      → Invalid: redirect to index.html

API Call
  → window.api.post('/endpoint', body)
    → api.js adds Authorization header from SessionManager
    → fetch() executes
    → 401 response → SessionManager.clearSession() + redirect
    → Success → caller processes response
```

---

## 2. Backend Architecture

FastAPI application with a flat module structure. All modules are imported directly into `main.py`.

```
main.py
  ├── Imports: auth, crypto, stego, audio_stego, video_stego, vault, audit, secure_notes
  ├── Middleware: CORSMiddleware (allow_origins=["*"])
  ├── Rate Limiters: login_limiter, master_pwd_limiter (in-memory RateLimiter)
  ├── File Validation: validate_file() (extension + 5MB size)
  └── Endpoints (see API_REFERENCE.md)
```

### Request Lifecycle

```
HTTP Request
  → CORSMiddleware (preflight or header injection)
  → Route handler
    → auth.get_current_user (JWT decode, DB user lookup)
    → validate_file() (if file upload)
    → Business logic (vault / notes / stego / audit)
      → crypto.encrypt/decrypt (with key_cache_context)
      → SQLAlchemy ORM operation
    → Response
```

---

## 3. Authentication Flow

```
POST /login (OAuth2PasswordRequestForm)
  → login_limiter.check(username)          ← Blocks after 5 failures
  → DB lookup: User by username
  → bcrypt.checkpw(password, hashed)
  → login_limiter.reset(username)          ← Clear failures on success
  → auth.create_access_token({"sub": username}, 30min)
  → Return: {access_token, token_type}

Client receives token
  → SessionManager.saveSession(token, username, raw_master_password)
  → Stored in sessionStorage (tab-scoped)

Subsequent requests
  → api.js reads SessionManager.getSession().token
  → Adds header: Authorization: Bearer <token>
  → auth.get_current_user() decodes JWT → DB user lookup → injects user object
```

---

## 4. Encryption Flow

### Backend (PyCryptodome — per-record)

```
encrypt_message(plaintext, master_password)
  → salt = random 16 bytes  (or from _active_salt context var)
  → key = PBKDF2(master_password, salt, dkLen=32, count=1_000_000)
  → cipher = AES(key, GCM mode)
  → ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
  → combined = salt(16) + nonce(16) + tag(16) + ciphertext
  → return base64(combined)

decrypt_message(payload_b64, master_password)
  → data = base64.decode(payload_b64)
  → salt = data[0:16], nonce = data[16:32], tag = data[32:48], ciphertext = data[48:]
  → key = PBKDF2(master_password, salt, ...)
  → cipher = AES(key, GCM, nonce=nonce)
  → return cipher.decrypt_and_verify(ciphertext, tag).decode()
```

Key insight: **every record has its own random salt embedded in the ciphertext**. There is no shared key. The master password is never stored.

### key_cache_context()

Used by `vault.py` and `secure_notes.py` to avoid re-deriving the key for every field in a single request. Within the context, `(password, salt)` pairs are cached in a `contextvars.ContextVar`.

---

## 5. Steganography Flow

### LSB Embedding (all three media types share the same logic)

```
Message → UTF-8 encode → bytes
  → 32-bit header (message byte length, big-endian)
  → Concat: [header_bits | message_bits]
  → For each bit: clear LSB of carrier byte; OR with message bit
  → Save output (PNG / WAV / AVI-FFV1 — all lossless)

Extraction:
  → Read first 32 bits from carrier → decode big-endian int = msg_len
  → Read next (msg_len × 8) bits
  → Pack bits → bytes → decode UTF-8 → return base64-encoded ciphertext
  → crypto.decrypt_message(ciphertext, password) → plaintext
```

Note: The stego layer embeds the **already-encrypted** ciphertext (from `crypto.encrypt_message`), not the raw message. The password used for stego embed/extract is **separate from the JWT master password** — it is a per-operation password entered in the stego UI.

---

## 6. Database Flow

```
Request arrives
  → get_db() yields a SQLAlchemy Session
  → Handler performs ORM operations (query / add / delete / commit)
  → Session is closed in finally block
  → Response returned

Tables:
  users → credentials (1:N)
  users → secure_notes (1:N)
  users → media_files (1:N)
  users → stego_operations (1:N)
  media_files → stego_operations (1:N)
```

---

## 7. Communication Flow

```
Browser (static files, no server)
        ↕ HTTP REST (JSON + multipart/form-data)
FastAPI (127.0.0.1:8000)
        ↕ SQLAlchemy ORM
SQLite (backend/pixelvault.db)
        ↕ File I/O
uploads/ directory (temporary stego files)
```

CORS is configured with `allow_origins=["*"]` — appropriate for local development. **Must be restricted in production.**
