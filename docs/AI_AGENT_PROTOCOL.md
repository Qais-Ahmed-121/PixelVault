# AI Agent Protocol — PixelVault

> **READ THIS FIRST.** Every AI development session must read this file before touching any code.

---

## 1. Documentation-First Workflow

1. Read `AI_AGENT_PROTOCOL.md` (this file).
2. Read `PROJECT_MANIFEST.md` for context and architecture.
3. Read the relevant section in `COMPONENT_INDEX.md` for the feature being changed.
4. Check `KNOWN_BUGS.md` and `TECHNICAL_DEBT.md` before introducing new patterns.
5. Implement the change.
6. Update `WORK_LOG.md` with what was done.
7. Update `CHANGELOG.md` with the version entry.
8. Update any affected documentation files (API_REFERENCE, COMPONENT_INDEX, etc.).

---

## 2. Token Optimization Rules

- **Do not scan the entire repository** unless explicitly asked. Use the docs in `/docs` as the primary knowledge source.
- **Read only targeted files.** Use `COMPONENT_INDEX.md` to identify which files are relevant.
- **Prefer `grep_search`** over full file views when locating a specific function or pattern.
- **Never read test files** unless the task is about testing.
- **Never read `venv/`** or `__pycache__/`.

---

## 3. File Selection Strategy

| Task | Files to read |
|---|---|
| Auth change | `auth.py`, `schemas.py`, `auth-service.js`, `session-manager.js` |
| Vault change | `vault.py`, `audit.py`, `vault.html`, `schemas.py` |
| Notes change | `secure_notes.py`, `notes.html`, `schemas.py` |
| Crypto change | `crypto.py` (backend), `crypto-service.js` (frontend — client-side only) |
| Stego change | `stego.py` / `audio_stego.py` / `video_stego.py`, `stego.html` |
| UI/Style change | `DESIGN_SYSTEM.md`, target `.html` file |
| API change | `main.py`, `schemas.py`, `API_REFERENCE.md` |
| DB schema change | `models.py`, `database.py`, `DATABASE_SCHEMA.md` |

---

## 4. Coding Standards

### Backend (Python / FastAPI)
- All endpoints require `Depends(auth.get_current_user)`.
- All sensitive data must be passed through `crypto.encrypt_message()` / `crypto.decrypt_message()` before DB storage.
- Use `crypto.key_cache_context()` for operations that encrypt/decrypt multiple fields in one request.
- All user text inputs must be sanitized via `html.escape()` before encryption.
- Rate limiting via `login_limiter` (login) and `master_pwd_limiter` (vault/notes) is mandatory.
- File uploads: always call `await validate_file(file)` first.

### Frontend (JavaScript)
- **Never use `localStorage` directly.** Use `window.SessionManager` for session state.
- **Never call `fetch()` directly.** Use `window.api.get()`, `window.api.post()`, `window.api.delete()`.
- **Never use `window.api.post()` with FormData for file uploads** — use `window.api.request()` directly to avoid double content-type headers.
- The `session.encryptionKey` field in `SessionManager` holds the **raw master password**, not a derived key. The backend derives its own keys per-record.
- Route guarding is automatic via `auth-service.js` — it runs `checkAuth()` on every page load.
- `CryptoService.deriveKey()` exists but is **not used in the current auth flow**. It is reserved for future client-side encryption features.

---

## 5. Security Standards

- **Never log passwords** or master passwords anywhere.
- **Never store the master password in `localStorage`** — only in `sessionStorage` (tab-scoped, cleared on tab close).
- JWT tokens expire in **30 minutes** (backend `ACCESS_TOKEN_EXPIRE_MINUTES`). Session manager mirrors this with a client-side expiry that slides on activity.
- The backend uses **ephemeral SECRET_KEY** if `.env` is missing — tokens will be invalidated on server restart. Always set `SECRET_KEY` in production.
- File upload validation: extension whitelist + 5MB hard limit (enforced client-side AND server-side).
- Brute-force protection: 5 failed attempts triggers a 15-minute lockout (in-memory, resets on server restart).

---

## 6. Documentation Update Policy

After any change to the following, update the corresponding doc:

| Changed | Update |
|---|---|
| Any endpoint | `API_REFERENCE.md` |
| Any DB model | `DATABASE_SCHEMA.md` |
| Any JS service | `FRONTEND_MODULES.md` |
| Any Python module | `BACKEND_MODULES.md` |
| Any bug found | `KNOWN_BUGS.md` |
| Any debt identified | `TECHNICAL_DEBT.md` |
| Session completed | `WORK_LOG.md` + `CHANGELOG.md` |

---

## 7. Forbidden Actions

- ❌ Do NOT use `localStorage` in any HTML file.
- ❌ Do NOT call `fetch()` directly — always use `window.api`.
- ❌ Do NOT pass a frontend-derived hex key as `master_password` to the backend.
- ❌ Do NOT delete or modify test files without explicit instruction.
- ❌ Do NOT add new Python dependencies without updating `requirements.txt`.
- ❌ Do NOT rename existing endpoints — they are consumed by frontend HTML files.
- ❌ Do NOT add CORS restrictions without testing all cross-origin flows.
- ❌ Do NOT bypass `validate_file()` for any file upload endpoint.
- ❌ Do NOT store unencrypted secrets in the database.

---

## 8. Recovery Procedure

If the application is broken:
1. Check `KNOWN_BUGS.md` for a documented fix.
2. Verify the backend is running: `GET http://127.0.0.1:8000/` should return `{"status": "online"}`.
3. Check `sessionStorage` in the browser DevTools — confirm `token`, `username`, `encryptionKey` are present.
4. Check browser console for `[API]` or `[AUTH]` errors.
5. Verify CORS is not blocking requests (look for preflight failures in the Network tab).

---

## 9. Checkpoint Procedure

At the end of each development session:
1. Append an entry to `WORK_LOG.md`.
2. Append a version entry to `CHANGELOG.md`.
3. Update `TODO.md` to mark completed items and add newly discovered items.
4. If the session introduced architectural changes, update `ARCHITECTURE.md`.
