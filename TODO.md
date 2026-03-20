# RBI FastAPI — TODO Checklist

> Work through layers in order — each layer depends on the one above it.
> Tick boxes as you go: change `[ ]` to `[x]`.

**Last reviewed: Session 16**
**Status snapshot:**
- Layer 0: ✅ Complete
- Layer 1: ✅ Complete (account_type Mapped[str] confirmed)
- Layer 2: 🟡 1/10 tests passing — injectdb.sql fixture + 8 remaining tests open
- Layer 3: ✅ Complete
- Layer 4: ❌ Empty — test_models.py not started
- Layer 5: ✅ Routes complete — ⚠️ soft delete re-query may return None (verify against schema.sql trigger)
- Layer 6: ❌ Not started
- Layer 7: ❌ Not started

**Next priority: Layer 2** — wire injectdb.sql fixture, then write remaining trigger tests in order.

---

---

## LAYER 0 — Project Setup

- [x] Confirm `pyproject.toml` has all dependencies — `fastapi`, `sqlalchemy`, `uvicorn`, `pydantic`, `pytest`, `python-dotenv`
- [x] Confirm `.env` has `DATABASE_URL` and any other config vars
- [x] Confirm `.gitignore` excludes `rbi.db`, `.env`, `__pycache__`
- [x] Confirm `uv.lock` is committed and reproducible

---

## LAYER 1 — `db/db.py`

- [x] Add `SessionLocal` — the session factory (`sessionmaker`)
- [x] Add `get_db()` — FastAPI dependency that yields a session and closes it after
- [x] Verify all 4 ORM models match `schema.sql` exactly — `account_type: Mapped[str]` confirmed ✅
- [x] Add `Base.metadata.create_all(engine)` call or confirm `schema.sql` handles creation
- [x] Enforce `PRAGMA foreign_keys = ON` at connection level via SQLAlchemy event listener

---

## LAYER 2 — `db/test_db.py`

- [x] Fixture: fresh **in-memory** test DB — never touch `rbi.db`
- [x] Fixture: run `schema.sql` against the test DB
- [ ] Fixture: inject seed data from `injectdb.sql` — not yet wired in
- [x] Test: valid transaction → trigger fires, balances update correctly
- [x] Test: transaction with insufficient funds → trigger raises, balances unchanged
- [x] Test: transaction to/from deactivated account → trigger raises
- [x] Test: delete account → trigger sets `activated=0`, row not actually deleted
- [x] Test: delete user → trigger deactivates user AND all child accounts


---

## LAYER 3 — `models/models.py`

> Pydantic schemas only — separate from SQLAlchemy ORM models in `db.py`

- [x] `UserCreate` — name
- [x] `UserResponse` — id, name, activated
- [x] `BankResponse` — id, name
- [x] `AccountCreate` — user_id, bank_id, account_type, balance
- [x] `AccountResponse` — all account fields safe to expose
- [x] `TransactionCreate` — from_id, to_id, amount
- [x] `TransactionResponse` — id, from_id, to_id, amount, transaction_time
- [x] Validator: amount must be > 0
- [x] Validator: account_type — `Literal['Savings', 'Current', 'Fixed Deposit', 'Salary']`
- [x] Validator: balance must be ≥ 0
- [x] `model_config = ConfigDict(from_attributes=True)` on all base models
- [x] `field_validator` on Create models only (not Base) — no double-conversion bug
- [x] `field_serializer` paise → rupees on output
- [x] rupees → paise on input via validator

---

## LAYER 4 — `models/test_models.py`

- [x] Test: `UserCreate` rejects empty name
- [ ] Test: `TransactionCreate` rejects amount ≤ 0
- [ ] Test: `AccountCreate` rejects invalid account_type
- [ ] Test: `AccountCreate` rejects negative balance
- [ ] Test: `UserResponse` correctly serialises from a SQLAlchemy ORM object
- [ ] Test: balance converts rupees → paise correctly on input
- [ ] Test: balance converts paise → rupees correctly on output

---

## LAYER 5 — `main.py`

- [x] FastAPI app initialised
- [x] `get_db` dependency wired in

**Users**
- [x] `POST   /users`
- [x] `GET    /users/{id}`
- [x] `DELETE /users/{id}` — soft delete via trigger — ⚠️ re-query after commit returns None (trigger deletes row, not soft-deletes — verify schema.sql trigger behaviour)
- [x] `GET    /users/{id}/accounts`

**Banks**
- [x] `GET    /banks` — list all banks
- [x] `GET    /banks/{id}`
- [x] `POST   /banks`
- [x] `GET    /banks/{id}/accounts`

**Accounts**
- [x] `POST   /accounts`
- [x] `GET    /accounts/{id}`
- [x] `DELETE /accounts/{id}` — soft delete via trigger — ⚠️ same re-query issue as users
- [x] `GET    /accounts/{id}/transactions`

**Transactions**
- [x] `POST   /transactions` — trigger handles balance updates
- [x] `GET    /transactions/{id}`
- [x] `IntegrityError` from trigger caught → returns 400 with trigger message

**Error handling**
- [x] All routes use `response_model=`
- [x] 404 on missing resources
- [x] 400 on trigger abort (insufficient funds, inactive account)
- [ ] `GET /users/{id}` — should also return user's accounts (currently returns user only)

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

3. **Tests use in-memory DB only.** `test_db.py` must never import or touch `rbi.db`. Use `sqlite:///:memory:`, run `schema.sql`, inject `injectdb.sql` as fixture. Production data must stay safe.

4. **Flush before FK children.** In test setup always `db.flush()` after inserting parent rows (bank, user) before inserting children (accounts). SQLAlchemy batching will otherwise violate FK constraints.

5. **Validators on Create only.** `field_validator` must live on `AccountCreate` / `TransactionCreate`, NOT on `AccountBase` / `TransactionBase`. Response models read raw paise from DB — running the validator on them doubles the value silently.