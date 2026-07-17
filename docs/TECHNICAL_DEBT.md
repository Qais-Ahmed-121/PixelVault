# Technical Debt — PixelVault

---

## 1. Architectural Boundaries

### Lack of Separation of Concerns (Frontend)
- **Problem:** HTML files contain large blocks of inline JavaScript. `stego.html`, `vault.html`, `notes.html`, `index.html`, and `audit.html` all bundle template rendering, event handling, logic, and style configuration directly inside `<script>` blocks.
- **Consequences:** Makes testing frontend components individually impossible. Promotes code duplication (such as toast utility functions and DOM element toggle helpers).
- **Remediation:** Extract page-specific inline JS into dedicated controller scripts (e.g. `vault-controller.js`, `stego-controller.js`) and load them in the HTML footer.

### Missing Service Layer (Backend)
- **Problem:** `main.py` directly handles database query construction, file writing, encryption calls, and Pydantic validation error raising inside route handlers.
- **Consequences:** Large, hard-to-test endpoint definitions.
- **Remediation:** Implement a service layer. Route handlers should delegate to a service module (e.g., `StegoService`, `UserService`) and only worry about receiving request schemas and returning responses.

---

## 2. Cryptography & Security Debt

### In-Memory Rate Limiting
- **Problem:** The brute-force protection logic (`RateLimiter` class in `main.py`) stores failures in a Python dictionary. Lockout history is lost on every server restart.
- **Consequences:** Attacker can reset rate limiting state by crashing the server or waiting for a deployment/restart. In a multi-worker deployment (e.g. uvicorn with `--workers`), the lockouts are not synchronized across workers.
- **Remediation:** Relocate lockout tracking to a persistent cache layer like Redis, or store it in a dedicated SQLite rate-limit table.

### Hardcoded Secret Key Fallback
- **Problem:** If `SECRET_KEY` is not present in `.env`, a random key is generated dynamically.
- **Consequences:** All active user sessions are invalidated immediately on uvicorn reload or restart.
- **Remediation:** Throw a boot-time error if `SECRET_KEY` is missing in production environments rather than generating a transient one.

---

## 3. Code Duplication

### Toast Notification System
- **Problem:** The `showToast` utility function is duplicated identically across:
  - `index.html`
  - `vault.html`
  - `notes.html`
  - `stego.html`
  - `generator.html`
  - `audit.html`
- **Consequences:** Maintenance overhead. A change to toast styling or behavior requires modifying 6 different HTML files.
- **Remediation:** Extract `showToast` into a common UI utility file (e.g., `ui-utils.js`) and load it in the header.

### Custom CSS Customizations
- **Problem:** Custom page styles are scattered across individual `<style>` blocks in each HTML page instead of being consolidated in a central stylesheet.
- **Consequences:** Fragile styling that deviates easily from the core design.
- **Remediation:** Centralize custom components (like glass tabs, circular progress gauges, and key-checklist rules) in a unified `/frontend/index.css`.

---

## 4. Performance & Scalability Debt

### Recomputing Scores on Every List
- **Problem:** `VaultManager.get_credentials` recomputes health scores and password reuse flags for every single credential record and commits the updates to the database on *every* read operation.
- **Consequences:** Unnecessary SQLite database write operations during list fetches. If the user has 100 credentials, 100 updates could occur on a simple read endpoint.
- **Remediation:** Only recompute and commit scores during write/edit operations (add or delete) and load static scores during simple list/read queries.

### Lack of Database Indexes on Foreign Keys
- **Problem:** `credentials.user_id`, `secure_notes.user_id`, `media_files.owner_id`, and `stego_operations.user_id` do not have database indexes defined in the ORM schema.
- **Consequences:** Full table scans on these tables when executing user queries as the database grows.
- **Remediation:** Add `index=True` to the foreign key columns in `models.py`.

---

## 5. Steganography Debt

### Lossless Codec Dependency for Video
- **Problem:** Video steganography depends strictly on OpenCV writing to `FFV1` codec in an AVI container.
- **Consequences:** FFV1 codecs may not be standard on client environments, leading to empty or unreadable video output if the server host lacks the necessary codec bindings. Large outputs exceed upload limits quickly.
- **Remediation:** Add fallback lossless video formats or implement client-side codec validation.

---

## 6. Testing & CI Debt

### Missing Automated Test Suite for Frontend
- **Problem:** No unit or integration tests exist for the frontend JavaScript files (`session-manager.js`, `api.js`, `auth-service.js`).
- **Consequences:** Manual testing is required to verify that authentication flows or token sliding logic do not break.
- **Remediation:** Introduce Vitest or Jest for JS unit testing and Playwright/Cypress for E2E tests.
