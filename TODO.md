# RBI FastAPI — TODO Checklist

> Work through layers in order — each layer depends on the one above it.
> Tick boxes as you go: change `[ ]` to `[x]`.

---

## LAYER 0 — Project Setup

- [ *] Confirm `pyproject.toml` has all dependencies — `fastapi`, `sqlalchemy`, `uvicorn`, `pydantic`, `pytest`, `python-dotenv`
- [ *] Confirm `.env` has `DATABASE_URL` and any other config vars
- [ *] Confirm `.gitignore` excludes `rbi.db`, `.env`, `__pycache__`
- [ *] Confirm `uv.lock` is committed and reproducible

---

## LAYER 1 — `db/db.py`

- [ *] Add `SessionLocal` — the session factory (`sessionmaker`)
- [ *] Add `get_db()` — FastAPI dependency that yields a session and closes it after
- [ ]* Verify all 4 ORM models match `schema.sql` exactly — column names, types, constraints
- [* ] Add `Base.metadata.create_all(engine)` call or confirm `schema.sql` handles creation
- [ *] Enforce `PRAGMA foreign_keys = ON` at connection level via SQLAlchemy event listener

---

## LAYER 2 — `db/test_db.py`

- [ ] Fixture: fresh **in-memory** test DB — never touch `rbi.db`
- [ ] Fixture: run `schema.sql` against the test DB
- [ ] Fixture: inject seed data from `ingectdb.sql`
- [ ] Test: create user → reads back correctly
- [ ] Test: create account → FK to user works
- [ ] Test: valid transaction → trigger fires, balances update correctly
- [ ] Test: transaction with insufficient funds → trigger raises, balances unchanged
- [ ] Test: transaction to/from deactivated account → trigger raises
- [ ] Test: delete account → trigger sets `activated=0`, row not actually deleted
- [ ] Test: delete user → trigger deactivates user AND all child accounts
- [ ] Test: overdraft cannot reduce balance below 0 (CHECK constraint)

---

## LAYER 3 — `models/models.py`

> Pydantic schemas only — separate from SQLAlchemy ORM models in `db.py`

- [ ] `UserCreate` — name
- [ ] `UserResponse` — id, name, activated, created_at
- [ ] `BankResponse` — id, name
- [ ] `AccountCreate` — user_id, bank_id, account_type, balance
- [ ] `AccountResponse` — all account fields safe to expose
- [ ] `TransactionCreate` — from_id, to_id, amount
- [ ] `TransactionResponse` — id, from_id, to_id, amount, transaction_time
- [ ] Validator: amount must be > 0
- [ ] Validator: account_type must be 1–4
- [ ] Validator: balance must be ≥ 0
- [ ] Add `model_config = ConfigDict(from_attributes=True)` on all response models

---

## LAYER 4 — `models/test_models.py`

- [ ] Test: `UserCreate` rejects empty name
- [ ] Test: `TransactionCreate` rejects amount ≤ 0
- [ ] Test: `AccountCreate` rejects invalid account_type
- [ ] Test: `AccountCreate` rejects negative balance
- [ ] Test: `UserResponse` correctly serialises from a SQLAlchemy ORM object

---

## LAYER 5 — `main.py`

- [ ] FastAPI app initialised
- [ ] `get_db` dependency wired in

**Users**
- [ ] `POST   /users`          — create user
- [ ] `GET    /users/{id}`     — get user + their accounts
- [ ] `DELETE /users/{id}`     — soft delete (trigger handles it)

**Banks**
- [ ] `GET    /banks`          — list all banks
- [ ] `GET    /banks/{id}`     — get bank details

**Accounts**
- [ ] `POST   /accounts`       — create account
- [ ] `GET    /accounts/{id}`  — get account
- [ ] `DELETE /accounts/{id}`  — soft delete

**Transactions**
- [ ] `POST   /transactions`          — insert into `transaction_history` (trigger does balance work — do NOT write SQLAlchemy balance logic here)
- [ ] `GET    /transactions/{account_id}` — get transaction history for an account

**Error handling**
- [ ] All routes use `response_model=` — no raw ORM objects returned
- [ ] All routes return correct HTTP status codes (400, 404, 422)
- [ ] Trigger `RAISE(ABORT, 'ERROR:...')` messages caught and returned as 400 with the trigger message

---

## LAYER 6 — Integration Tests

- [ ] End-to-end: create user → create account → perform transaction → verify balance updated
- [ ] End-to-end: transaction with insufficient funds → 400 returned, balances unchanged
- [ ] End-to-end: delete user → all accounts deactivated → transaction to that account returns 400

---

## LAYER 7 — Deployment

- [ ] `README.md` updated — setup instructions, env vars, how to run
- [ ] `pyproject.toml` has no stdlib packages (`re`, `sqlite3`)
- [ ] App runs cleanly with `uvicorn main:app`
- [ ] Deploy to Render or Railway
- [ ] Live URL added to README and resume

---

## ⚠️ Critical Reminders

> Read before writing any code.

1. **Trigger owns balance updates.** The `transactions` trigger in `schema.sql` handles all balance changes. SQLAlchemy must only insert into `transaction_history` — never update balances directly. Any SQLAlchemy balance logic = double-update bug.

2. **`PRAGMA foreign_keys = ON` per connection.** SQLite disables FK enforcement by default. Must be set via a SQLAlchemy connection event listener in `db.py` — without it, invalid FKs are silently accepted and tests pass incorrectly.

3. **Tests use in-memory DB only.** `test_db.py` must never import or touch `rbi.db`. Use `sqlite:///:memory:`, run `schema.sql`, inject `ingectdb.sql` as fixture. Production data must stay safe.
