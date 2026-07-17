# Roadmap — PixelVault

---

## 🟥 High Priority

- [ ] **Remove duplicate DB:** Clean up root-level `/pixelvault.db` to prevent developer confusion and verify that `/backend/pixelvault.db` is the single source of truth.
- [ ] **Secure Vault Generator:** Replace the insecure `Math.random()` password generator logic inside `vault.html` with cryptographically secure `window.crypto.getRandomValues()` values.
- [ ] **Lockout Persistence:** Migrate the memory-based brute-force tracker in `main.py` to store failure attempts and timestamps in a database table or Redis cache.
- [ ] **Production Secret Verification:** Raise a critical boot error if `SECRET_KEY` is not defined in the environment config rather than silently falling back to a temporary random key.

---

## 🟨 Medium Priority

- [ ] **Centralize UI Utilities:** Extract identical `showToast()` UI notifications and panel toggle helper logic from the pages into a single `ui-utils.js` asset.
- [ ] **Alembic Integration:** Configure Alembic for SQLite schema migrations so model updates can be applied without dropping tables.
- [ ] **Verify Stego Download Types:** Update the `/stego/download/{id}` endpoint to map `file_type` to correct content-type header values and file extensions rather than hardcoding `image/png`.
- [ ] **Long Password Pre-hashing:** Address bcrypt's 72-byte string limitation by pre-hashing user passwords using SHA-256 before invoking the bcrypt validation function.

---

## 🟩 Low Priority

- [ ] **Mobile Navbar Navigation:** Add mobile support to the global header by designing a responsive hamburger menu interface.
- [ ] **Client-Side Note Encryption:** Wire `CryptoService.deriveKey()` into notes management to support local-only client-side note storage before uploading to the server database.
- [ ] **Database Foreign Key Indexes:** Add explicit columns indexes to relationships (`credentials.user_id`, `secure_notes.user_id`, etc.) to improve query lookups as tables grow.
