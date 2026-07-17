# Backend Modules — PixelVault

---

## `main.py` — Application Entry Point

**Responsibility:** FastAPI app definition, all API routes, middleware, file validation, and rate limiting.

**Key elements:**
- `app = FastAPI(title="PixelVault API", version="1.0.0")`
- CORSMiddleware: `allow_origins=["*"]` (dev-only setting)
- `UPLOAD_DIR = "uploads"`, `MAX_FILE_SIZE = 5MB`, `ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".wav", ".mp4", ".avi"}`
- `validate_file(file)` — reads up to MAX_FILE_SIZE+1 bytes to check size; resets stream with `await file.seek(0)`
- `RateLimiter` class — in-memory per-key attempt counter with sliding 15-min window
- `login_limiter`, `master_pwd_limiter` — module-level instances

**Imports all business modules:** `auth, crypto, stego, audio_stego, video_stego, vault, audit, secure_notes`

---

## `auth.py` — Authentication Module

**Responsibility:** JWT token management, bcrypt password hashing, user retrieval dependency.

| Function | Description |
|---|---|
| `get_password_hash(password)` | `bcrypt.hashpw(pass.encode(), bcrypt.gensalt()).decode()` |
| `verify_password(plain, hashed)` | `bcrypt.checkpw(plain.encode(), hashed.encode())` |
| `create_access_token(data, expires_delta)` | HS256 JWT with `exp` claim |
| `get_current_user(token, db)` | FastAPI dependency — decodes JWT, queries DB, returns User |

**Config:** `SECRET_KEY` from `.env` (falls back to random ephemeral), `ALGORITHM = "HS256"`, `ACCESS_TOKEN_EXPIRE_MINUTES = 30`

**External:** `python-jose` (JWT), `bcrypt` (hashing), `pydantic-settings` (env loading)

---

## `crypto.py` — Cryptography Module

**Responsibility:** AES-256-GCM symmetric encryption/decryption with PBKDF2 key derivation.

| Function | Description |
|---|---|
| `derive_key(password, salt)` | PBKDF2-SHA256, 1M iterations, 32-byte output. Caches result in request context. |
| `encrypt_message(message, password)` | Generate salt → derive key → AES-GCM encrypt → base64(salt+nonce+tag+ciphertext) |
| `decrypt_message(payload_b64, password)` | base64 decode → extract salt/nonce/tag → derive key → AES-GCM decrypt+verify |
| `key_cache_context()` | Context manager that sets up a request-scoped key derivation cache via `contextvars` |

**Exceptions:** `CryptoError` — raised on encrypt/decrypt failures.

**External:** `pycryptodome` (`Crypto.Cipher.AES`, `Crypto.Protocol.KDF.PBKDF2`)

---

## `database.py` — Database Module

**Responsibility:** SQLAlchemy engine, session factory, dependency.

- `SQLALCHEMY_DATABASE_URL = "sqlite:///./pixelvault.db"` — relative to CWD (must run from `/backend`)
- `engine = create_engine(url, connect_args={"check_same_thread": False})`
- `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`
- `Base = declarative_base()`
- `get_db()` — generator dependency that yields a session and closes it in `finally`

---

## `models.py` — ORM Models

**Responsibility:** SQLAlchemy table definitions.

| Model | Table | Key Fields |
|---|---|---|
| `User` | `users` | id, username, email, hashed_password, is_active, created_at |
| `MediaFile` | `media_files` | id, filename, filepath, file_type, owner_id, created_at |
| `StegoOperation` | `stego_operations` | id, operation_type, description, user_id, media_file_id, created_at |
| `Credential` | `credentials` | id, service_name*, username*, password*, url*, notes*, health_score, is_reused, user_id |
| `SecureNote` | `secure_notes` | id, title*, content*, user_id |

*Encrypted fields (AES-256-GCM ciphertext stored as base64 string)

---

## `schemas.py` — Pydantic Schemas

**Responsibility:** Request/response validation, serialization.

| Schema | Purpose |
|---|---|
| `UserCreate` | Register — validates password complexity |
| `UserOut` | User response (no password) |
| `Token` | Login response |
| `TokenData` | JWT payload |
| `StegoHistoryOut` | History list item |
| `ExtractionResult` | Stego extract response |
| `CredentialCreate` | Add vault credential (includes master_password) |
| `CredentialOut` | Credential response |
| `VaultListRequest` | `{master_password}` for list/audit/export |
| `CredentialUpdate` | Partial update schema (not currently exposed as endpoint) |
| `SecureNoteCreate` | Add note (includes master_password) |
| `SecureNoteOut` | Note response |
| `NotesListRequest` | `{master_password}` for notes list |

---

## `vault.py` — Vault Manager

**Responsibility:** Credential CRUD with field-level encryption, health scoring, CSV export.

| Method | Description |
|---|---|
| `sanitize_data(data)` | `html.escape()` wrapper |
| `encrypt_vault_item(data, pwd)` | Single field encryption |
| `decrypt_vault_item(data, pwd)` | Single field decryption |
| `_recompute_scores(db, db_creds, decrypted_list)` | Recalculates health_score and is_reused for all credentials; persists to DB if changed |
| `create_credential(db, cred, user_id, pwd)` | Sanitize → encrypt all fields → store → compute initial health score |
| `get_credentials(db, user_id, pwd)` | Fetch all → decrypt → recompute scores → return list[dict] |
| `delete_credential(db, cred_id, user_id)` | Owner-scoped delete |
| `generate_csv_export(credentials)` | Format decrypted list as CSV string |

---

## `audit.py` — Audit Engine

**Responsibility:** Password security analysis.

| Method | Description |
|---|---|
| `check_strength(password)` | 0–100 score: length(+30), uppercase(+20), lowercase(+10), digit(+20), special(+20) |
| `analyze_vault(credentials)` | Full vault scan: avg strength - reuse penalty; returns health_score, alerts, stats |

**Health score formula:**
```
avg_strength = sum(check_strength(pwd)) / count
reuse_penalty = min(reused_count * 10, 50)
overall_health = max(0, int(avg_strength - reuse_penalty))
```

---

## `secure_notes.py` — Notes Manager

**Responsibility:** Encrypted note CRUD.

| Method | Description |
|---|---|
| `sanitize(data)` | `html.escape()` |
| `create_note(db, note, user_id, pwd)` | Sanitize → encrypt title + content → store |
| `get_notes(db, user_id, pwd)` | Fetch all → decrypt each (silently skip failures) → return list[dict] |
| `delete_note(db, note_id, user_id)` | Owner-scoped delete |

---

## `stego.py` — Image Steganography

**Responsibility:** LSB hide/extract for PNG images.

| Function | Description |
|---|---|
| `msg_to_bits(bytes)` | `np.unpackbits()` — bytes to bit array |
| `bits_to_msg(bits)` | `np.packbits().tobytes()` — bit array to bytes |
| `hide_message(image_path, message, output_path)` | Embed: header + message bits into pixel LSBs → save PNG |
| `extract_message(image_path)` | Extract: read header → read message bits → decode UTF-8 |

**Exception:** `StegoError`

---

## `audio_stego.py` — Audio Steganography

**Responsibility:** LSB hide/extract for WAV files.

| Function | Description |
|---|---|
| `hide_message(audio_path, message, output_path)` | WAV frames → bytearray → embed bits → write WAV |
| `extract_message(audio_path)` | Read WAV frames → extract header → extract message |

**Exception:** `AudioStegoError`
**Limitation:** PCM WAV only.

---

## `video_stego.py` — Video Steganography

**Responsibility:** Frame-by-frame LSB hide/extract for video files.

| Function | Description |
|---|---|
| `hide_message(video_path, message, output_path)` | OpenCV capture → FFV1 AVI writer → embed bits across frames |
| `extract_message(video_path)` | Capture → read header from frame 0 → collect bits across frames |

**Exception:** `VideoStegoError`
**Output codec:** FFV1 (lossless)

---

## `generator.py` — Password Generator

**Responsibility:** Cryptographically secure password generation.

| Method | Description |
|---|---|
| `generate_random(length, uppercase, numbers, symbols)` | `secrets.choice()` — guaranteed at least one of each type |
| `generate_smart(keyword, length)` | Leet-speak transformation + random padding |

**Note:** This class is not wired to any HTTP endpoint. The frontend `generator.html` implements its own client-side password generator in JavaScript.

---

## `benchmark_vault.py` — Performance Benchmark

**Responsibility:** Test/benchmarking script for vault encryption performance.
**Status:** Not imported by `main.py`. Run standalone only.
