# Known Bugs — PixelVault

---

## Bug Registry

| ID | Severity | Status | Title |
|---|---|---|---|
| BUG-001 | 🔴 CRITICAL (Fixed) | RESOLVED | Frontend-derived hex key passed as master_password to backend |
| BUG-002 | 🟡 MEDIUM (Fixed) | RESOLVED | Stray closing braces in vault.html unlockVault() |
| BUG-003 | 🟠 HIGH | OPEN | Rate limiter resets on server restart |
| BUG-004 | 🟡 MEDIUM | OPEN | Duplicate pixelvault.db at project root |
| BUG-005 | 🟡 MEDIUM | OPEN | generator.py PasswordGenerator not wired to any API endpoint |
| BUG-006 | 🟡 MEDIUM | OPEN | Password generator in vault.html uses Math.random() (not crypto-secure) |
| BUG-007 | 🟠 HIGH | OPEN | No HTTPS — all traffic is plaintext |
| BUG-008 | 🟡 MEDIUM (Fixed) | RESOLVED | user.is_active field is stored but never checked during auth |
| BUG-009 | 🔴 HIGH | OPEN | No database migration system — schema changes require DB drop/recreate |
| BUG-010 | 🟡 MEDIUM | OPEN | stego/download endpoint uses hardcoded media_type "image/png" regardless of file type |
| BUG-011 | 🟢 LOW | OPEN | No mobile navigation — hamburger menu not implemented |
| BUG-012 | 🟡 MEDIUM | OPEN | bcrypt 72-byte truncation risk for very long passwords |

---

## Detail Records

### BUG-001 — Frontend hex key as master_password ✅ FIXED
- **Severity:** Critical
- **Files:** `auth-service.js`
- **Description:** `AuthService.login()` was calling `CryptoService.deriveKey()` and storing the resulting hex string as `encryptionKey` in `SessionManager`. When `vault.html`, `notes.html`, and `audit.html` passed `session.encryptionKey` as `master_password` to backend endpoints, the backend received a hex string instead of the raw password. `PBKDF2(hex_string, random_salt)` produced a completely different key than `PBKDF2(raw_password, random_salt)`, causing all decrypt operations to fail silently.
- **Fix:** `AuthService.login()` now stores the raw master password directly as `encryptionKey`. The `CryptoService.deriveKey()` call was removed from the login flow.
- **Session:** Resolved in the centralized auth session.

### BUG-002 — Stray braces in vault.html ✅ FIXED
- **Severity:** Medium (syntax error — JavaScript broke silently)
- **Files:** `vault.html`
- **Description:** During the refactor of `unlockVault()`, the try/catch block was removed but two stray closing braces `}` remained, causing a syntax error in the inline script.
- **Fix:** Stray braces removed.

### BUG-003 — Rate limiter memory reset
- **Severity:** High
- **Files:** `main.py` (RateLimiter class)
- **Description:** Rate limiter state is stored in process memory (`self._store: dict`). Any server restart (uvicorn reload, crash, deployment) resets all lockout counters. An attacker can bypass brute-force protection by triggering server restarts.
- **Recommendation:** Persist rate limit state to Redis or SQLite.

### BUG-004 — Duplicate database file
- **Severity:** Medium
- **Files:** `/pixelvault.db` (root), `/backend/pixelvault.db`
- **Description:** Two database files exist. The backend uses `sqlite:///./pixelvault.db` (relative to CWD = `/backend`). The root-level file is likely a stale artifact from running `main.py` from the wrong directory.
- **Recommendation:** Delete root-level `pixelvault.db`. Add `pixelvault.db` to `.gitignore`.

### BUG-005 — generator.py not exposed via API
- **Severity:** Medium
- **Files:** `backend/generator.py`
- **Description:** `PasswordGenerator` class exists but is not imported in `main.py` and has no API endpoint. The frontend generator is completely client-side.
- **Recommendation:** Either expose it via a `POST /generate` endpoint or remove the file and rely on the frontend implementation.

### BUG-006 — Vault add-modal uses Math.random()
- **Severity:** Medium
- **Files:** `vault.html` → `generateRandomPass()`
- **Description:** The "generate password" button in the add-credential modal uses `Math.random()` which is not cryptographically secure. For a password manager, this is inappropriate.
- **Recommendation:** Replace with `crypto.getRandomValues()`.

### BUG-007 — No HTTPS
- **Severity:** High
- **Files:** `main.py` (Uvicorn config), all frontend pages
- **Description:** API runs on `http://127.0.0.1:8000`. All data, including JWT tokens and (encrypted) payloads, transmitted in plaintext.
- **Recommendation:** Add TLS via nginx reverse proxy or Uvicorn SSL for any non-localhost deployment.

### BUG-008 — is_active field unused ✅ FIXED
- **Severity:** Medium
- **Files:** `models.py`, `auth.py`
- **Description:** `User.is_active` defaults to `True` but was never checked in `get_current_user()`. Accounts could not be suspended.
- **Fix:** Added `if not user.is_active:` check to `get_current_user` dependency in `auth.py`. If a suspended or inactive user attempts to call protected endpoints, a standard HTTP 401 Unauthorized exception is raised.


### BUG-009 — No schema migration system
- **Severity:** High
- **Files:** `database.py`, `models.py`
- **Description:** No Alembic or migration tool. `Base.metadata.create_all()` only creates missing tables — it does not apply column changes, renames, or index additions.
- **Recommendation:** Initialize Alembic.

### BUG-010 — Wrong media_type in stego download
- **Severity:** Medium
- **Files:** `main.py` → `download_stego_image()`
- **Description:** The download endpoint always returns `media_type="image/png"` and `filename="pixelvault_download.png"` regardless of whether the file is WAV or AVI.
- **Recommendation:** Look up `media_file.file_type` and set media_type + filename accordingly.

### BUG-011 — No mobile navigation
- **Severity:** Low
- **Files:** All HTML pages (navbar)
- **Description:** Navigation links are horizontal and collapse on small screens with no hamburger menu fallback.

### BUG-012 — bcrypt 72-byte truncation
- **Severity:** Medium
- **Files:** `auth.py` → `get_password_hash()`
- **Description:** bcrypt silently truncates passwords at 72 bytes. Passwords longer than 72 characters have identical hashes regardless of trailing characters.
- **Recommendation:** Add a note in user-facing UI or pre-hash with SHA-256 before bcrypt.
