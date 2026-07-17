# Changelog — PixelVault

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.1] - 2026-07-16

### Added
- **User Activation Verification:** Added `user.is_active` check inside the backend authentication middleware dependency (`get_current_user` in `auth.py`).

### Security Improvements
- Suspended or inactive user accounts are now immediately rejected with a standard `401 Unauthorized` response when attempting to call protected endpoints.

### Backward Compatibility Notes
- Fully backward compatible. Existing active user accounts remain unaffected.

---

## [1.1.0] - 2026-07-16

### Changed
- **Unified Session Management:** Migrated application frontend from fragmented `localStorage` persistence to transient `sessionStorage` session lifetimes (handled by centralized `SessionManager`).
- **Standardized API Request Client:** Replaced all native, scattered `fetch()` calls in the HTML pages with requests executed through `window.api` (`api.js`). Added automatic Bearer token injection and global 401 response handling.
- **Backend Key Derivation Compatibility:** Corrected frontend key derivation flow in `auth-service.js` to store the raw master password string in session memory. Since the backend derives its own PBKDF2 keys using per-record unique random salts, passing a derived hex key from the frontend was breaking compatibility. The frontend now correctly passes the raw master password.
- **Route Guarding:** Injected automatic auth check logic (`checkAuth`) in `auth-service.js` that runs on all page loads to prevent access to protected dashboard pages if no session is active.
- **Unified Logout:** Replaced inline `localStorage.removeItem` cleanups with a centralized `window.AuthService.logout()` call on all pages.

### Fixed
- Fixed vault unlocking bug in `vault.html` where syntax errors (stray closing braces) were breaking scripts.
- Fixed a decrypt/unlock error on the Notes page where the frontend derived hex key was passed to the backend instead of the raw master password.
- Fixed audit connection errors by routing requests through the global API client rather than manual fetch calls.

---

## [1.0.0] - 2024-11-20

### Added
- Core steganography modules for hiding and extracting encrypted messages in PNG (image), WAV (audio), and AVI (video) formats.
- Password Vault feature with credential storage, encryption-at-rest (AES-256-GCM), and strength auditing.
- Secure Notes feature with field-level encryption.
- Multi-mode client-side password generator (random and keyword-based).
- SQLite storage backend with SQLAlchemy ORM support.
- User management with JWT bearer authentication and bcrypt password hashing.
- API validation utilizing Pydantic schemas.
