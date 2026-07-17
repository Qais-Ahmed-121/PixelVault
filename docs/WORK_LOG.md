# Work Log — PixelVault

---

## Current Project State Checkpoint (Iteration 0.5) — ✅ COMPLETE
- **Task:** Project Rebranding (StegaVault → PixelVault) — **DONE**
- **Project Rename:** Rebrand the application from StegaVault to PixelVault.
- **Old Name:** StegaVault
- **New Name:** PixelVault
- **Files Expected to Change:**
  - `README.md`
  - `RUNNING.md`
  - `PROJECT_REPORT.md`
  - `backend/main.py`
  - `backend/database.py`
  - `backend/stego.py`
  - `backend/audio_stego.py`
  - `backend/video_stego.py`
  - `backend/crypto.py`
  - `backend/test_stego_roundtrip.py`
  - `frontend/index.html`
  - `frontend/dashboard.html`
  - `frontend/vault.html`
  - `frontend/notes.html`
  - `frontend/audit.html`
  - `frontend/stego.html`
  - `frontend/generator.html`
  - `docs/AI_AGENT_PROTOCOL.md`
  - `docs/PROJECT_MANIFEST.md`
  - `docs/ARCHITECTURE.md`
  - `docs/COMPONENT_INDEX.md`
  - `docs/CHANGELOG.md`
  - `docs/WORK_LOG.md`
  - `docs/TODO.md`
  - `docs/TECHNICAL_DEBT.md`
  - `docs/STEGANOGRAPHY.md`
  - `docs/RELEASE_REPORT.md`
  - `docs/KNOWN_BUGS.md`
  - `docs/FRONTEND_MODULES.md`
  - `docs/DIRECTORY_STRUCTURE.md`
  - `docs/DESIGN_SYSTEM.md`
  - `docs/DEPENDENCY_GRAPH.md`
  - `docs/DATABASE_SCHEMA.md`
- **Potential Risks:**
  - Database filepath change (e.g. `stegavault.db` -> `pixelvault.db`): changing this URL could result in a blank database, but all tables are created automatically on startup, so the risk is low, and compatibility is maintained.
  - Front-end / back-end communication references (e.g., custom file download names or test messages): ensured that these are renamed consistently to prevent mismatches.

---

## Current Project State Checkpoint (Iteration 1)
- **Current Task:** Centralize user active status authentication validation (resolving BUG-008) and harden backend authentication middleware by ensuring inactive users are rejected with standard JSON responses rather than being allowed to access protected endpoints.
- **Planned Implementation:** Modify `backend/auth.py`'s `get_current_user` function to inspect the `user.is_active` field. Raise standard FastAPI HTTP 401/403 exceptions for inactive users, which guarantees a consistent JSON error response and avoids HTML pages.
- **Files to be modified:**
  - `backend/auth.py`
- **Dependencies:** `FastAPI Depends`, `SQLAlchemy models.User`
- **Possible Risks:** None identified. This is a secure validation enhancement that protects endpoints.

---

## Current Project State
The project has successfully finished the refactoring of its authentication architecture and session management. Legacy `localStorage` storage strategies and direct `fetch()` calls have been replaced with a unified, service-based model. Backend integration for encryption operations (vault, notes, audit, stego) has been verified. The backend performs PBKDF2 key derivation using per-record unique random salts, and the frontend correctly stores and passes the raw master password to support this.

---

## Completed Tasks

### Iteration 1: Authentication & Session Management Refactoring (Centralized Session & Security Hardening)
- **User Activation Verification:** Added `user.is_active` validation in the backend security dependency (`auth.py` -> `get_current_user`). Any suspended/deactivated user account is now rejected with a standard JSON 401 response instead of allowing access.
- **Verification:** Ran and passed the complete backend test suite (`test_stage10.py`, `test_stage11.py`, `test_stage12.py`, `test_stage13.py`, and `test_stego_roundtrip.py`).
- **Files Modified:**
  - `backend/auth.py` (added is_active validation)
  - `docs/KNOWN_BUGS.md` (marked BUG-008 as resolved)
  - `docs/CHANGELOG.md` (updated version history to 1.1.1)
  - `docs/WORK_LOG.md` (this file)

### Legacy Phase 1 & 2: Authentication & Session Hardening
- Created `SessionManager` in `session-manager.js` to manage session details transiently in `sessionStorage` (with a sliding 30-minute expiration).
- Implemented global `api` client wrapper in `api.js` to automatically inject authorization headers and manage token expiries.
- Created `AuthService` in `auth-service.js` to unify register, login, logout, and client-side page-level route guarding.
- Eliminated all legacy direct `localStorage` reads/writes across all HTML pages.
- Corrected the key derivation design mismatch: replaced the derived client-side hex key with the raw master password in `sessionStorage` to match the backend's PBKDF2 implementation.

### Legacy Phase 2: Page Integration Refactoring
- Refactored `vault.html` to load/audit/export/delete credentials using the global `api` client and `SessionManager` state.
- Refactored `notes.html` to decrypt and list notes using the centralized `api` client.
- Refactored `audit.html` to run health audits utilizing the centralized session.
- Refactored `stego.html` to hide/extract payloads via the global API client and pull download/clear actions through the same client.
- Refactored `generator.html` to cleanly call the centralized logout routine.

### Legacy Phase 3: Project Documentation
- Initialized documentation suite in `/docs` containing the AI agent protocol, architecture guide, schema layouts, API reference sheets, and known bug trackers.

---

## Known Limitations
- The brute-force protection rate limiter in `main.py` is in-memory and resets on server restarts.
- Plaintext HTTP is used for local hosting; production deployment requires TLS/HTTPS configuration.

---

## Recommended Next Steps / Iteration 2
1. **Remove Stale Root Database:** The root-level `stegavault.db` file is locked by a running backend process. Stop the server, delete it, and confirm only `backend/pixelvault.db` exists.
2. **Implement Rate Limiter Persistence:** Move the rate limiter store into SQLite.
3. **Upgrade Password Generator Entropy:** Replace `Math.random()` in `vault.html`'s inline generator with `window.crypto.getRandomValues()`.

---

## Iteration 0.5 Completion Summary (Code-Level Rebranding)
- **Date:** 2026-07-17
- **Scope:** Full source-code, documentation, and configuration rebranding from StegaVault → PixelVault.
- **Files Modified:**
  - `README.md`, `RUNNING.md`, `PROJECT_REPORT.md`
  - `backend/main.py` — API title, health check message, all 5 download filenames
  - `backend/database.py` — SQLite URL changed to `pixelvault.db`
  - `backend/stego.py`, `audio_stego.py`, `video_stego.py`, `crypto.py` — test block strings
  - `backend/test_stego_roundtrip.py` — baseline test message
  - `frontend/index.html`, `dashboard.html`, `vault.html`, `notes.html`, `audit.html`, `stego.html`, `generator.html` — `<title>` tags, navbar logos, download filenames
  - `backend/stegavault.db` → renamed to `backend/pixelvault.db`
  - `.gitignore` — expanded to cover `*.db`, `venv/`, `__pycache__/`, `uploads/`
- **Tests:** All 5 stego round-trip tests pass (✅ 5/5).
