# Dependency Graph — PixelVault

---

## Backend Module Dependencies

```
main.py
  ├── database.py        (engine, Base, get_db)
  ├── models.py          (ORM models)
  ├── schemas.py         (Pydantic schemas)
  ├── auth.py            (JWT, bcrypt, get_current_user)
  │     └── models.py
  │     └── schemas.py
  │     └── database.py
  ├── crypto.py          (AES-GCM, PBKDF2)
  ├── stego.py           (image LSB)
  ├── audio_stego.py     (audio LSB)
  ├── video_stego.py     (video LSB)
  ├── vault.py
  │     ├── models.py
  │     ├── schemas.py
  │     ├── crypto.py
  │     └── audit.py     ← vault.py imports AuditEngine directly
  ├── audit.py
  │     └── models.py
  └── secure_notes.py
        ├── models.py
        ├── schemas.py
        └── crypto.py
```

**Note:** `audit.py` is imported by both `main.py` (for the `/vault/audit` endpoint) and `vault.py` (for `_recompute_scores()`). This creates an indirect dependency: `main.py → vault.py → audit.py` (in addition to `main.py → audit.py` directly).

---

## Frontend Module Dependencies

```
Every protected HTML page
  └── session-manager.js   (no deps — uses sessionStorage directly)
  └── crypto-service.js    (no deps — uses window.crypto)
  └── api.js
        └── session-manager.js   (reads SessionManager.getSession())
  └── auth-service.js
        ├── api.js               (login, register calls)
        ├── session-manager.js   (saveSession, clearSession, getSession)
        └── crypto-service.js    (was used; now unused in current flow)

Page inline scripts
  └── window.api           (all API calls)
  └── window.SessionManager (getSession on DOMContentLoaded)
  └── window.AuthService   (logout)
```

---

## Python Package Dependencies

| Package | Version | Used By |
|---|---|---|
| `fastapi` | 0.104.1 | `main.py` |
| `uvicorn[standard]` | 0.24.0 | `main.py` (server) |
| `sqlalchemy` | 2.0.23 | `database.py`, `models.py`, all managers |
| `python-jose[cryptography]` | 3.3.0 | `auth.py` (JWT) |
| `passlib[bcrypt]` | 1.7.4 | Declared but bcrypt is called directly |
| `bcrypt` | 4.0.1 | `auth.py` |
| `python-multipart` | 0.0.6 | `main.py` (file upload form parsing) |
| `pillow` | 10.1.0 | `stego.py` (image processing) |
| `numpy` | 1.26.2 | `stego.py`, `audio_stego.py`, `video_stego.py` |
| `pycryptodome` | 3.19.0 | `crypto.py` (AES, PBKDF2) |
| `pydantic` | 2.5.2 | `schemas.py`, `auth.py` |
| `pydantic-settings` | 2.1.0 | `auth.py` (env loading) |
| `email-validator` | 2.1.0 | `schemas.py` (EmailStr) |
| `opencv-python` | 4.8.1.78 | `video_stego.py` |

---

## Frontend External Dependencies

| Library | Version | Source | Used by |
|---|---|---|---|
| Tailwind CSS | Latest (CDN) | `https://cdn.tailwindcss.com` | All HTML pages |
| Google Fonts — Outfit | Latest | Google Fonts CDN | All HTML pages |

No npm packages, no build tools.

---

## Shared Utilities

| Utility | Shared Between |
|---|---|
| `crypto.encrypt_message` | `vault.py`, `secure_notes.py`, `main.py` (stego embed) |
| `crypto.decrypt_message` | `vault.py`, `secure_notes.py`, `main.py` (stego extract) |
| `crypto.key_cache_context` | `vault.py`, `secure_notes.py` |
| `auth.get_current_user` | Every protected endpoint in `main.py` |
| `validate_file()` | All 6 embed/extract endpoints in `main.py` |
| `AuditEngine.check_strength` | `audit.py` (analyze_vault), `vault.py` (_recompute_scores, create_credential) |
| `window.api` | All page inline scripts |
| `window.SessionManager` | `api.js`, `auth-service.js`, all page inline scripts |

---

## Potential Circular Dependency Risk

`vault.py` imports from `audit.py`:
```python
from audit import AuditEngine
```

`main.py` imports both:
```python
import vault, audit
```

There is no circular dependency currently because `audit.py` does **not** import from `vault.py`. The dependency is one-directional: `vault → audit`. This is safe.

---

## Isolated Modules (No Upstream Consumers)

| Module | Status |
|---|---|
| `generator.py` | Not imported by `main.py`. Python class unused in API. |
| `benchmark_vault.py` | Standalone script. Not imported anywhere. |
| `test_stage*.py` | Test files. Not imported by production code. |
| `test_stego_roundtrip.py` | Test file. Not imported by production code. |
