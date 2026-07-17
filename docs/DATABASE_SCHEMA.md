# Database Schema — PixelVault

Database: SQLite — `backend/pixelvault.db`
ORM: SQLAlchemy 2.0
Init: `Base.metadata.create_all(bind=engine)` on startup (no migration system)

---

## Table: `users`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | Integer | PK, indexed | Auto-increment |
| `username` | String | UNIQUE, NOT NULL, indexed | 3–50 chars (Pydantic) |
| `email` | String | UNIQUE, NOT NULL, indexed | Valid email format |
| `hashed_password` | String | NOT NULL | bcrypt hash |
| `is_active` | Boolean | default=True | Not currently used for access control |
| `created_at` | DateTime (TZ) | server_default=now() | |

**Relationships:**
- `media_files` → `MediaFile` (1:N)
- `operations` → `StegoOperation` (1:N)
- `credentials` → `Credential` (1:N)
- `secure_notes` → `SecureNote` (1:N)

---

## Table: `credentials`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | Integer | PK, indexed | |
| `service_name` | String | NOT NULL | **Encrypted** (AES-256-GCM) |
| `username` | String | NOT NULL | **Encrypted** |
| `password` | String | NOT NULL | **Encrypted** |
| `url` | String | nullable | **Encrypted** if present |
| `totp_secret` | String | nullable | **Encrypted** if present |
| `notes` | String | nullable | **Encrypted** if present |
| `health_score` | Integer | default=100 | Recomputed on each list call |
| `is_reused` | Boolean | default=False | Recomputed on each list call |
| `created_at` | DateTime (TZ) | server_default=now() | |
| `updated_at` | DateTime (TZ) | server_default=now(), onupdate=now() | |
| `user_id` | Integer | FK → users.id | |

**Notes:** All string fields are stored as base64-encoded AES-GCM ciphertext. The raw values are never in the DB.

---

## Table: `secure_notes`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | Integer | PK, indexed | |
| `title` | String | NOT NULL | **Encrypted** |
| `content` | String | NOT NULL | **Encrypted** |
| `created_at` | DateTime (TZ) | server_default=now() | |
| `updated_at` | DateTime (TZ) | server_default=now(), onupdate=now() | |
| `user_id` | Integer | FK → users.id | |

---

## Table: `media_files`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | Integer | PK, indexed | |
| `filename` | String | NOT NULL | UUID-based filename |
| `filepath` | String | NOT NULL | Absolute path to file in `uploads/` |
| `file_type` | String | | `"png"`, `"wav"`, `"video"` |
| `owner_id` | Integer | FK → users.id | |
| `created_at` | DateTime (TZ) | server_default=now() | |

**Relationships:**
- `operations` → `StegoOperation` (1:N)

---

## Table: `stego_operations`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | Integer | PK, indexed | |
| `operation_type` | String | | `"hide_image"`, `"hide_audio"`, `"hide_video"`, `"extract_image"`, `"extract_audio"`, `"extract_video"` |
| `description` | String | | Human-readable log message |
| `user_id` | Integer | FK → users.id | |
| `media_file_id` | Integer | FK → media_files.id, nullable | Null for extract operations |
| `created_at` | DateTime (TZ) | server_default=now() | |

---

## Entity Relationship Summary

```
users (1) ─────────────────────────────── (N) credentials
users (1) ─────────────────────────────── (N) secure_notes
users (1) ─────────────────────────────── (N) media_files
users (1) ─────────────────────────────── (N) stego_operations
media_files (1) ────────────────────────── (N) stego_operations
```

---

## Constraints & Notes

- **No explicit unique indexes** beyond `users.username` and `users.email`.
- **No foreign key cascade rules** defined in ORM — deleting a user does not automatically delete their records.
- **No schema migration tool** (Alembic) is configured. Schema changes require dropping and recreating the DB, or manual ALTER TABLE.
- `is_active` on `User` is stored but never checked during authentication — it could be used for account suspension in a future iteration.
