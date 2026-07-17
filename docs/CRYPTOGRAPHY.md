# Cryptography — PixelVault

---

## 1. Overview

PixelVault uses **AES-256-GCM** with **PBKDF2-SHA256** key derivation for all data encryption at rest (vault credentials and secure notes). The steganography layer also encrypts payloads before embedding.

Library: **PyCryptodome** (`pycryptodome==3.19.0`)
Module: `backend/crypto.py`

---

## 2. Key Derivation

### Function: `derive_key(password: str, salt: bytes) -> bytes`

```
PBKDF2(
    password = master_password (str),
    salt     = random 16-byte value (per-record),
    dkLen    = 32 bytes (256-bit key),
    count    = 1,000,000 iterations,
    hmac_hash_module = SHA256
)
→ 32-byte AES key
```

**Key properties:**
- Each record has its own **independent random salt** (embedded in ciphertext).
- 1,000,000 PBKDF2 iterations provides strong resistance to brute-force attacks.
- The derived key is **never stored** — it is derived on each request.
- The master password is **never stored** — only used transiently during encryption/decryption.

### Key Cache Context

```python
with crypto.key_cache_context():
    # Multiple encrypt/decrypt calls in this block
    # reuse the derived key for the same (password, salt) pair
```

Implemented using `contextvars.ContextVar` — the cache is request-scoped and does not leak across concurrent requests. Used in `vault.py` and `secure_notes.py` to avoid re-deriving keys for every field.

---

## 3. Encryption

### Function: `encrypt_message(message: str, password: str) -> str`

```
1. salt = random 16 bytes  (from _active_salt context var, or freshly generated)
2. key  = derive_key(password, salt)
3. cipher = AES.new(key, AES.MODE_GCM)
4. ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
5. combined = salt[16] + cipher.nonce[16] + tag[16] + ciphertext[N]
6. return base64.b64encode(combined).decode()
```

**Output format (base64-encoded binary):**

```
| Offset | Length | Content |
|--------|--------|---------|
| 0      | 16     | Salt (random per-record) |
| 16     | 16     | GCM Nonce (random per cipher instance) |
| 32     | 16     | GCM Authentication Tag |
| 48     | N      | Ciphertext |
```

Total overhead: 48 bytes + plaintext length, then base64 (~33% size increase).

---

## 4. Decryption

### Function: `decrypt_message(encrypted_payload: str, password: str) -> str`

```
1. data = base64.decode(encrypted_payload)
2. Validate: len(data) >= 48
3. salt       = data[0:16]
4. nonce      = data[16:32]
5. tag        = data[32:48]
6. ciphertext = data[48:]
7. key = derive_key(password, salt)
8. cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
9. plaintext = cipher.decrypt_and_verify(ciphertext, tag)
10. return plaintext.decode('utf-8')
```

If the password is wrong or the data is corrupted:
- `decrypt_and_verify()` raises `ValueError` (GCM tag mismatch).
- `crypto.py` catches it and raises `CryptoError("Decryption failed: Invalid password or corrupted data")`.
- Callers in `main.py` catch this and raise HTTP 401.

---

## 5. Frontend Crypto Service

File: `frontend/crypto-service.js`
Class: `CryptoService`

Implements PBKDF2 key derivation using the **Web Crypto API**:
```javascript
CryptoService.deriveKey(password, username)
  → PBKDF2(SHA-256, 100,000 iterations, salt = username.toLowerCase())
  → Returns hex string (64 chars = 256 bits)
```

**Current status:** This function is **not used in the current authentication flow**. The session's `encryptionKey` field stores the raw master password (not a derived key) for compatibility with the backend's per-record random salt approach.

`CryptoService` is reserved for potential future features such as client-side encryption before upload, or local note encryption.

---

## 6. Stego Encryption

When embedding a secret message via steganography:

```
User enters: plaintext message + stego password
  → crypto.encrypt_message(plaintext, stego_password)
  → Returns base64 ciphertext
  → stego.hide_message(image_path, ciphertext, output_path)
```

The stego password is **separate** from the user's master password — it is entered per-operation in the steganography UI and is not stored anywhere.

When extracting:
```
stego.extract_message(image_path) → base64 ciphertext
  → crypto.decrypt_message(ciphertext, stego_password)
  → Returns plaintext message
```

---

## 7. Threat Model

| Threat | Mitigation |
|---|---|
| Database theft | All sensitive data encrypted with AES-256-GCM — attacker needs master password |
| Master password brute-force (offline) | PBKDF2 with 1M iterations makes brute-force extremely slow |
| Master password brute-force (online) | Rate limiter: 5 failures → 15-min lockout |
| JWT theft | Short expiry (30 min), sessionStorage (tab-scoped) |
| XSS | Input sanitized via `html.escape()` before encryption; CSP not configured |
| MITM | No HTTPS in current setup — transport layer unprotected in dev |
| GCM tag forgery | PyCryptodome's `decrypt_and_verify()` is authenticated — tampering detected |
| Replay attacks | GCM nonce is random per operation — not replayed |
| Credential reuse across sites | Reuse detection in `AuditEngine` flags repeated passwords |

---

## 8. Known Cryptographic Limitations

1. **No HTTPS** — all traffic is plaintext on localhost. Deployment requires TLS.
2. **bcrypt 72-byte truncation** — passwords longer than 72 bytes are silently truncated.
3. **Frontend PBKDF2 uses username as salt** — unlike the backend which uses random salts per record, the frontend's `CryptoService` uses the lowercase username as a fixed salt. This reduces the strength of client-side derived keys if they were ever used.
4. **Stego password not validated for complexity** — any string can be used as a stego operation password.
5. **No key rotation mechanism** — if the master password changes, all encrypted records must be re-encrypted.
