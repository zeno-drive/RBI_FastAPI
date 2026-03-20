# RBI Banking System — FastAPI

A banking operations REST API built with FastAPI, SQLAlchemy ORM, and SQLite3. Features ACID-compliant SQLite triggers for balance management and soft-deletion, a Pydantic validation layer with rupees/paise conversion, and a React frontend served directly from the API.

**Live:** https://rbi-fastapi.onrender.com

---

## Features

- **Trigger-driven balance updates** — SQLite triggers handle all fund transfers, insufficient funds checks, and inactive account validation. SQLAlchemy never touches balances directly.
- **Soft deletion** — DELETE on users and accounts fires a trigger that sets `activated=0` instead of removing the row. Cascade: deleting a user deactivates all their accounts.
- **Pydantic validation layer** — rupees → paise on input, paise → rupees on output. Validators on Create models only to prevent double-conversion.
- **Internal operations dashboard** — React frontend (CDN, no build step) with dropdowns, reactivation, transaction history, and live balance display.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| ORM | SQLAlchemy 2.0 (mapped_column style) |
| Database | SQLite3 with triggers |
| Validation | Pydantic v2 |
| Testing | Pytest + in-memory SQLite |
| Frontend | React 18 via CDN (single HTML file) |
| Package manager | uv |
| Deployment | Render (Singapore) |

---

## Project Structure

```
RBI_FastAPI/
├── app.py              # FastAPI routes
├── schema.sql          # DB schema + triggers
├── injectdb.sql        # Seed data (30 banks, 32 users, 35 accounts)
├── db/
│   ├── db.py           # SQLAlchemy engine, ORM models, get_db()
│   └── test_db.py      # Trigger + ORM tests (5 passing)
├── models/
│   ├── models.py       # Pydantic schemas
│   └── test_models.py  # Pydantic validation tests (6 passing)
├── static/
│   └── index.html      # React frontend
├── pyproject.toml
└── uv.lock
```

---

## Setup

**Requirements:** Python 3.12+, uv

```bash
# Clone
git clone https://github.com/zeno-drive/RBI_FastAPI.git
cd RBI_FastAPI

# Install dependencies
uv sync

# Run
uvicorn app:app --reload
```

Open http://localhost:8000 — redirects to the dashboard UI.
API docs at http://localhost:8000/docs.

---

## Seed Data

To populate the database with sample data (30 Indian banks, 32 users, 35 accounts, 35 transactions):

```bash
sqlite3 rbi.db < injectdb.sql
```

> Note: `injectdb.sql` values are stored in paise. Do not re-insert via the API — the validator will double-convert.

---

## API Reference

### Users
| Method | Route | Description |
|---|---|---|
| `POST` | `/users` | Create user |
| `GET` | `/users` | List all users (pagination: `?skip=0&limit=100`) |
| `GET` | `/users/{id}` | Get user by ID |
| `GET` | `/users/{id}/accounts` | Get all accounts for user |
| `DELETE` | `/users/{id}` | Soft-delete user + deactivate all accounts |
| `PATCH` | `/users/{id}/reactivate` | Reactivate user |

### Banks
| Method | Route | Description |
|---|---|---|
| `POST` | `/banks` | Create bank |
| `GET` | `/banks` | List all banks |
| `GET` | `/banks/{id}` | Get bank by ID |
| `GET` | `/banks/{id}/accounts` | Get all accounts in bank |

### Accounts
| Method | Route | Description |
|---|---|---|
| `POST` | `/accounts` | Create account |
| `GET` | `/accounts` | List all accounts (pagination: `?skip=0&limit=100`) |
| `GET` | `/accounts/{id}` | Get account by ID |
| `GET` | `/accounts/{id}/transactions` | Get transaction history for account |
| `DELETE` | `/accounts/{id}` | Soft-delete account |
| `PATCH` | `/accounts/{id}/reactivate` | Reactivate account |

### Transactions
| Method | Route | Description |
|---|---|---|
| `POST` | `/transactions` | Transfer funds (trigger validates + updates balances) |
| `GET` | `/transactions/{id}` | Get transaction by ID |

---

## Trigger Behaviour

All three triggers are defined in `schema.sql`:

**`transactions` (BEFORE INSERT on transaction_history)**
Raises `ABORT` if:
- Sending account is inactive
- Receiving account is inactive
- Sending account has insufficient funds

On success: deducts `amount` from `from_id` balance, adds to `to_id` balance.

**`deactivate_account` (BEFORE DELETE on accounts)**
Sets `activated=0` on the row. Raises `IGNORE` to cancel the actual delete.

**`deactivate_user_and_child_accounts` (BEFORE DELETE on users)**
Sets `activated=0` on the user. Sets `activated=0` on all accounts where `user_id = OLD.id`. Raises `IGNORE` to cancel the actual delete.

---

## Currency

All amounts stored internally in **paise** (integer). API input/output in **rupees** (float).

- Input: `field_validator(mode="before")` on `AccountCreate` and `TransactionCreate` — multiplies by 100
- Output: `field_serializer` on `AccountBase` and `TransactionBase` — divides by 100

---

## Tests

```bash
# All tests
pytest

# DB trigger tests only
pytest db/test_db.py -v

# Pydantic model tests only
pytest models/test_models.py -v
```

11 tests total — 5 trigger tests, 6 model tests. All passing.

---

## Deployment

Deployed on Render (Singapore region) with auto-deploy on push to `main`.

**Build command:** `pip install uv && uv sync`
**Start command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`

> Free tier spins down after 15 minutes of inactivity. First request after sleep takes ~30 seconds.
