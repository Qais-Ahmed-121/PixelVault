# API Reference — PixelVault

Base URL: `http://127.0.0.1:8000`

Auth: All protected endpoints require `Authorization: Bearer <token>` header.

---

## Health Check

### `GET /`
- **Auth:** None
- **Response:** `{"status": "online", "message": "...", "version": "1.0.0"}`

---

## Authentication

### `POST /register`
- **Auth:** None
- **Body:** JSON `{ username, email, password }`
- **Validation:** username (3–50 chars), email (valid format), password (8–128 chars, must contain uppercase, lowercase, digit, special char)
- **Response:** `UserOut` — `{id, username, email, is_active, created_at}`
- **Errors:** 400 `Username already registered` | 400 `Email already registered` | 422 validation errors

### `POST /login`
- **Auth:** None
- **Body:** `application/x-www-form-urlencoded` (OAuth2PasswordRequestForm) — `username`, `password`
- **Rate limit:** 5 failures per 15 min per username → HTTP 429
- **Response:** `{access_token, token_type: "bearer"}`
- **Errors:** 401 `Incorrect username or password` | 429 `Too many failed attempts`

### `GET /users/me`
- **Auth:** Required
- **Response:** `UserOut`

---

## Steganography — Embed

### `POST /embed/image` (alias: `POST /stego/hide`)
- **Auth:** Required
- **Body:** `multipart/form-data` — `file` (image), `message` (str), `password` (str)
- **Validation:** file ≤ 5MB, extension in {.png, .jpg, .jpeg, .wav, .mp4, .avi}, message non-empty
- **Processing:** `crypto.encrypt_message(message, password)` → `stego.hide_message()` → saved as UUID.png
- **Response:** File download — `image/png`
- **Side effects:** Creates `MediaFile` + `StegoOperation` records

### `POST /embed/audio`
- **Auth:** Required
- **Body:** `multipart/form-data` — `file` (.wav), `message`, `password`
- **Validation:** file ≤ 5MB, must be `.wav`
- **Processing:** encrypt → `audio_stego.hide_message()` → UUID.wav
- **Response:** File download — `audio/wav`

### `POST /embed/video`
- **Auth:** Required
- **Body:** `multipart/form-data` — `file` (.mp4 or .avi), `message`, `password`
- **Validation:** file ≤ 5MB, must be `.mp4` or `.avi`
- **Processing:** encrypt → `video_stego.hide_message()` → UUID.avi (FFV1 lossless)
- **Response:** File download — `video/x-msvideo`

---

## Steganography — Extract

### `POST /extract/image` (alias: `POST /stego/extract`)
- **Auth:** Required
- **Body:** `multipart/form-data` — `file` (PNG with hidden payload), `password`
- **Processing:** `stego.extract_message()` → `crypto.decrypt_message(payload, password)`
- **Response:** `{message: "decrypted text"}`
- **Errors:** 400 if extraction or decryption fails

### `POST /extract/audio`
- **Auth:** Required
- **Body:** `multipart/form-data` — `file` (.wav), `password`
- **Response:** `{message: "decrypted text"}`
- **Errors:** 400 `Failed to extract secret...` | 500 on unhandled exception

### `POST /extract/video`
- **Auth:** Required
- **Body:** `multipart/form-data` — `file` (.avi), `password`
- **Response:** `{message: "decrypted text"}`
- **Errors:** 400 if extraction fails

---

## Stego History

### `GET /stego/history`
- **Auth:** Required
- **Response:** `List[StegoHistoryOut]` — `[{id, operation_type, description, created_at, media_file_id}]`

### `GET /stego/download/{media_file_id}`
- **Auth:** Required
- **Path param:** `media_file_id` (int)
- **Response:** File download — owner-scoped
- **Errors:** 404 if not found or file missing from disk

### `DELETE /stego/history/{history_id}`
- **Auth:** Required
- **Path param:** `history_id` (int)
- **Response:** `{detail: "Log entry sanitized successfully"}`
- **Errors:** 404 if not found

### `DELETE /stego/history/clear`
- **Auth:** Required
- **Response:** `{detail: "All logs shredded cleanly"}`

---

## Password Vault

### `POST /vault/add`
- **Auth:** Required
- **Body:** JSON `{service_name, username, password, url?, totp_secret?, notes?, master_password}`
- **Validation:** service_name/username/password (1+ chars), master_password (8+ chars)
- **Processing:** XSS sanitize + encrypt each field → store `Credential` row
- **Response:** `CredentialOut` — includes `health_score`, `is_reused`
- **Errors:** 400 on failure

### `POST /vault/list`
- **Auth:** Required
- **Body:** JSON `{master_password}`
- **Rate limit:** `master_pwd_limiter` (5 failures → lockout)
- **Processing:** decrypt all credentials → recompute health scores → persist updates
- **Response:** `List[dict]` — decrypted credential objects
- **Errors:** 401 `Invalid master password`

### `DELETE /vault/delete/{cred_id}`
- **Auth:** Required
- **Path param:** `cred_id` (int)
- **Response:** `{message: "Credential deleted successfully"}`
- **Errors:** 404 if not found

### `POST /vault/audit`
- **Auth:** Required
- **Body:** JSON `{master_password}`
- **Rate limit:** `master_pwd_limiter`
- **Processing:** get_credentials → AuditEngine.analyze_vault()
- **Response:** `{health_score, alerts: [{type, service, severity}], stats: {total, weak, reused}}`
- **Errors:** 401 `Audit failed. Verify master password.`

### `POST /vault/export`
- **Auth:** Required
- **Body:** JSON `{master_password}`
- **Rate limit:** `master_pwd_limiter`
- **Response:** CSV file download (`pixelvault_backup.csv`)
- **Errors:** 401 on failure

---

## Secure Notes

### `POST /notes/add`
- **Auth:** Required
- **Body:** JSON `{title, content, master_password}`
- **Validation:** title (1–200 chars), content (1–5000 chars), master_password (8+ chars)
- **Processing:** sanitize + encrypt title + content → store `SecureNote`
- **Response:** `SecureNoteOut` — `{id, title, content, created_at, updated_at}`
- **Errors:** 400 on failure

### `POST /notes/list`
- **Auth:** Required
- **Body:** JSON `{master_password}`
- **Rate limit:** `master_pwd_limiter`
- **Response:** `List[dict]` — decrypted notes (failures are silently skipped)
- **Errors:** 401 `Invalid master password`

### `DELETE /notes/delete/{note_id}`
- **Auth:** Required
- **Path param:** `note_id` (int)
- **Response:** `{message: "Note deleted successfully"}`
- **Errors:** 404 if not found
