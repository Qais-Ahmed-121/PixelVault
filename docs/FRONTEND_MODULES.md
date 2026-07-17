# Frontend Modules — PixelVault

---

## Service Layer

All service scripts are loaded in every protected HTML page in this order:

```html
<script src="session-manager.js"></script>
<script src="crypto-service.js"></script>
<script src="api.js"></script>
<script src="auth-service.js"></script>
```

They expose globals: `window.SessionManager`, `window.CryptoService`, `window.api`, `window.AuthService`.

---

## `session-manager.js` — Session State

**Global:** `window.SessionManager`

Manages the active user session in `sessionStorage`. Provides a sliding 30-minute expiry that refreshes on each `getSession()` call.

| Method | Description |
|---|---|
| `saveSession(token, username, encryptionKey)` | Writes token, username, encryptionKey, sessionExpiry to sessionStorage. Removes stale localStorage keys. |
| `getSession()` | Returns `{token, username, encryptionKey}` if valid; `null` if missing or expired. Slides expiry on success. |
| `clearSession()` | Removes all session keys from sessionStorage and legacy localStorage. |
| `isValid()` | Returns `true` if `getSession()` is non-null. |

**Key contract:** `encryptionKey` stores the **raw master password** (not a derived hex key). This value is passed directly as `master_password` in API requests to vault and notes endpoints.

---

## `crypto-service.js` — Client-Side Cryptography

**Global:** `window.CryptoService`

Implements PBKDF2 key derivation using the browser's Web Crypto API.

| Method | Description |
|---|---|
| `deriveKey(password, username)` | PBKDF2-SHA256, 100,000 iterations, salt = `username.trim().toLowerCase()` encoded to bytes. Returns 64-char hex string. |

**Current status:** This module is loaded on all pages but is **not used in the current session flow**. It was initially intended to store a derived key in sessionStorage instead of the raw password — but this conflicts with the backend's per-record random salt approach.

Reserved for future use cases: client-side encryption of local data, or pre-upload encryption.

---

## `api.js` — HTTP Client

**Global:** `window.api`

Centralized `fetch` wrapper. Automatically injects `Authorization: Bearer` token from `SessionManager` and handles global 401 errors.

| Method | Signature | Description |
|---|---|---|
| `request(endpoint, options)` | Low-level | Full control. Auth header auto-injected. 401 → clear session + redirect. |
| `get(endpoint, headers?)` | `GET` | Basic GET request. |
| `post(endpoint, body, headers?)` | `POST` | JSON body (auto-stringified) or FormData (no Content-Type override). |
| `delete(endpoint, headers?)` | `DELETE` | Basic DELETE request. |

**Important:** For multipart `FormData` (file uploads), use `window.api.request()` directly with `method: 'POST'` and `body: formData`. Using `window.api.post()` with FormData works but avoids double serialization.

**Base URL:** Defined in `api.js` as `const API_URL = "http://127.0.0.1:8000"`. Change here to update all pages.

---

## `auth-service.js` — Authentication Service

**Global:** `window.AuthService`

Coordinates login, registration, logout, and page-level route guarding.

| Method | Description |
|---|---|
| `login(username, password)` | POST to `/login` (FormData), calls `SessionManager.saveSession()`, returns token data |
| `register(username, email, password)` | POST JSON to `/register`, returns user data |
| `logout()` | Calls `SessionManager.clearSession()`, redirects to `index.html` |
| `checkAuth()` | Route guard: redirects unauthenticated users from protected pages; redirects authenticated users away from login page |

`checkAuth()` runs automatically on every page via:
```javascript
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => window.AuthService.checkAuth());
} else {
    window.AuthService.checkAuth();
}
```

---

## Page Scripts

Each HTML page contains an inline `<script>` block with page-specific logic. All page scripts follow the same pattern:

```javascript
// 1. Auto-unlock if session is valid
document.addEventListener("DOMContentLoaded", async () => {
    const session = window.SessionManager.getSession();
    if (session) {
        currentMasterPassword = session.encryptionKey;
        await loadXxx();
    }
});

// 2. Manual unlock (lock overlay form)
async function unlockXxx() {
    const pwd = document.getElementById('master-pwd').value;
    if (!pwd) return showToast("...", "error");
    currentMasterPassword = pwd;
    await loadXxx();
}

// 3. Load data via API client
async function loadXxx() {
    const res = await window.api.post('/xxx/list', { master_password: currentMasterPassword });
    // ... render
}

// 4. Logout
function logout() { window.AuthService.logout(); }

// 5. Toast utility (inline per page)
function showToast(message, type) { /* ... */ }
```

---

## `index.html` — Login / Registration

- Tab switcher: `showTab('login')` / `showTab('register')` toggles form visibility
- Login: `AuthService.login()` → redirect to `dashboard.html`
- Register: `AuthService.register()` → auto-login after success
- Password checklist: real-time regex validation on `input` event
- Error display: parses backend Pydantic errors (string or array) into human-readable messages

---

## `dashboard.html` — Navigation Hub

- Displays username from `SessionManager.getSession().username`
- Navigation cards linking to all feature pages
- Logout button calls `AuthService.logout()`

---

## `vault.html` — Password Vault

- Lock overlay → `unlockVault()` → `loadVault()`
- `loadVault()` calls `/vault/audit` + `/vault/list` simultaneously → populates stats + credential grid
- Credential grid: `renderCredentials(creds)` → HTML template with show/hide toggle, copy button, delete button
- Event listeners attached after render (not inline `onclick`) to avoid CSP issues
- Add credential modal: form submit → `window.api.post('/vault/add', data)`
- Password generator: `generateRandomPass()` fills add-modal input (client-side, uses `Math.random` not `crypto.getRandomValues`)
- Export: `window.api.post('/vault/export', ...)` → `res.blob()` → download

---

## `notes.html` — Secure Notes

- Lock overlay → `unlockNotes()` → `loadNotes()`
- `loadNotes()` → `window.api.post('/notes/list', ...)` → render accordion-style note list
- Add note form → `window.api.post('/notes/add', ...)`
- Delete: `window.api.delete('/notes/delete/{id}')`

---

## `audit.html` — Security Audit

- Lock overlay → `runAudit()` → `window.api.post('/vault/audit', ...)`
- Auto-runs on `DOMContentLoaded` if session exists
- Renders: health score ring (conic-gradient), alert cards (WEAK_PASSWORD, REUSED_PASSWORD), stat badges

---

## `stego.html` — Steganography

- Mode switcher: `setMode(mode)` — updates file input accept attributes and active tab UI
- Embed: `handleEmbed()` → FormData → `window.api.request('/embed/{mode}', {method:'POST', body: formData})`
- Extract: `handleExtract()` → FormData → `window.api.request('/extract/{mode}', ...)` → display result
- History: `loadHistory()` → `window.api.get('/stego/history')` → render table
- Download: `downloadFile(id)` → `window.api.get('/stego/download/{id}')` → blob download
- Delete log: `deleteSingleHistory(id)` → `window.api.delete('/stego/history/{id}')`
- Clear all: `clearAllHistory()` → `window.api.delete('/stego/history/clear')`
- Client-side preflight: 5MB size check before sending (prevents socket drop)

---

## `generator.html` — Password Generator

- Fully client-side — no API calls
- Controls: length slider, character type toggles (uppercase, numbers, symbols)
- `generatePassword()` — builds charset from toggles, uses `Math.random()` (not cryptographically secure — UX tool only)
- Copy button
- Logout calls `window.AuthService.logout()`
