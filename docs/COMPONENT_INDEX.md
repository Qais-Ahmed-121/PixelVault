# Component Index — PixelVault

Use this file to quickly identify which files are involved in any feature.

---

## Authentication & Session

| Aspect | Files |
|---|---|
| **Frontend service** | `auth-service.js`, `session-manager.js`, `api.js` |
| **Backend logic** | `auth.py` |
| **Schemas** | `schemas.py` → `UserCreate`, `UserOut`, `Token`, `TokenData` |
| **Models** | `models.py` → `User` |
| **Endpoints** | `POST /register`, `POST /login`, `GET /users/me` |
| **UI** | `index.html` |
| **Dependencies** | `python-jose`, `bcrypt`, `pydantic-settings` |

---

## Password Vault

| Aspect | Files |
|---|---|
| **Frontend UI** | `vault.html` |
| **Backend manager** | `vault.py` → `VaultManager` |
| **Schemas** | `schemas.py` → `CredentialCreate`, `CredentialOut`, `VaultListRequest`, `CredentialUpdate` |
| **Models** | `models.py` → `Credential` |
| **Endpoints** | `POST /vault/add`, `POST /vault/list`, `DELETE /vault/delete/{id}`, `POST /vault/audit`, `POST /vault/export` |
| **Services** | `crypto.py` (encrypt/decrypt), `audit.py` (health scoring) |
| **Dependencies** | `pycryptodome` |

---

## Secure Notes

| Aspect | Files |
|---|---|
| **Frontend UI** | `notes.html` |
| **Backend manager** | `secure_notes.py` → `NotesManager` |
| **Schemas** | `schemas.py` → `SecureNoteCreate`, `SecureNoteOut`, `NotesListRequest` |
| **Models** | `models.py` → `SecureNote` |
| **Endpoints** | `POST /notes/add`, `POST /notes/list`, `DELETE /notes/delete/{id}` |
| **Services** | `crypto.py` |

---

## Security Audit

| Aspect | Files |
|---|---|
| **Frontend UI** | `audit.html` |
| **Backend engine** | `audit.py` → `AuditEngine` |
| **Schemas** | `schemas.py` → `VaultListRequest` |
| **Endpoints** | `POST /vault/audit` |
| **Services** | `vault.py` (get_credentials), `crypto.py` (decrypt) |

---

## Steganography — Image

| Aspect | Files |
|---|---|
| **Frontend UI** | `stego.html` (mode: image) |
| **Backend** | `stego.py` → `hide_message()`, `extract_message()` |
| **Endpoints** | `POST /embed/image`, `POST /extract/image`, legacy alias `POST /stego/hide` + `POST /stego/extract` |
| **Services** | `crypto.py` (encrypts message before embed / decrypts after extract) |
| **Dependencies** | `pillow`, `numpy` |

---

## Steganography — Audio

| Aspect | Files |
|---|---|
| **Frontend UI** | `stego.html` (mode: audio) |
| **Backend** | `audio_stego.py` → `hide_message()`, `extract_message()` |
| **Endpoints** | `POST /embed/audio`, `POST /extract/audio` |
| **Services** | `crypto.py` |
| **Dependencies** | `wave` (stdlib), `numpy` |

---

## Steganography — Video

| Aspect | Files |
|---|---|
| **Frontend UI** | `stego.html` (mode: video) |
| **Backend** | `video_stego.py` → `hide_message()`, `extract_message()` |
| **Endpoints** | `POST /embed/video`, `POST /extract/video` |
| **Services** | `crypto.py` |
| **Dependencies** | `opencv-python`, `numpy` |

---

## Stego History & File Management

| Aspect | Files |
|---|---|
| **Frontend UI** | `stego.html` → `loadHistory()`, `downloadFile()`, `deleteSingleHistory()`, `clearAllHistory()` |
| **Models** | `models.py` → `StegoOperation`, `MediaFile` |
| **Schemas** | `schemas.py` → `StegoHistoryOut`, `ExtractionResult` |
| **Endpoints** | `GET /stego/history`, `GET /stego/download/{id}`, `DELETE /stego/history/{id}`, `DELETE /stego/history/clear` |

---

## Password Generator

| Aspect | Files |
|---|---|
| **Frontend UI** | `generator.html` (client-side only — no API calls) |
| **Backend** | `generator.py` → `PasswordGenerator.generate_random()`, `generate_smart()` |
| **Note** | `generator.py` is **not wired to any endpoint**. The frontend generator is fully client-side JavaScript. The Python class exists but is unused in the API. |

---

## Database & ORM

| Aspect | Files |
|---|---|
| **Engine/Session** | `database.py` |
| **Models** | `models.py` |
| **Migrations** | None — `Base.metadata.create_all()` on startup |

---

## Cryptography

| Aspect | Files |
|---|---|
| **Backend** | `crypto.py` → `encrypt_message()`, `decrypt_message()`, `derive_key()`, `key_cache_context()` |
| **Frontend** | `crypto-service.js` → `CryptoService.deriveKey()` (Web Crypto PBKDF2 — currently unused in auth flow) |

---

## File Upload & Validation

| Aspect | Files |
|---|---|
| **Backend** | `main.py` → `validate_file()`, `ALLOWED_EXTENSIONS`, `MAX_FILE_SIZE` |
| **Frontend** | `stego.html` → client-side pre-flight size check (5MB) and accept attribute per mode |

---

## Rate Limiting

| Aspect | Files |
|---|---|
| **Implementation** | `main.py` → `RateLimiter` class |
| **Login limiter** | `login_limiter` — keyed by username, applied to `POST /login` |
| **Master password limiter** | `master_pwd_limiter` — keyed by user ID, applied to `/vault/list`, `/vault/audit`, `/vault/export`, `/notes/list` |
| **Config** | `MAX_ATTEMPTS = 5`, `LOCKOUT_WINDOW = 15` minutes |
