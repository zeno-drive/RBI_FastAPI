# RBI FastAPI — TODO Checklist

> Work through layers in order — each layer depends on the one above it.
> Tick boxes as you go: change `[ ]` to `[x]`.

**Last reviewed: Session 17**
**Status snapshot:**
- Layer 0: ✅ Complete
- Layer 1: ✅ Complete
- Layer 2: ✅ Complete — 5/5 trigger tests passing
- Layer 3: ✅ Complete — `Business` account type added
- Layer 4: ✅ Complete — 6/6 model tests passing
- Layer 5: ✅ Complete — all routes + redirect / → /docs
- Layer 6: ⏭️ Skipped — covered by Layer 2 trigger tests
- Layer 7: 🟡 In progress — deployed to Render ✅, README + resume pending

**Next priority: Layer 7** — write README, verify pyproject.toml, add live URL to resume.

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
- [x] Fixture: inject seed data — skipped, tests build their own data ✅
- [x] Test: valid transaction → trigger fires, balances update correctly ✅
- [x] Test: transaction with insufficient funds → trigger raises, balances unchanged ✅
- [x] Test: transaction to/from deactivated account → trigger raises ✅
- [x] Test: delete account → trigger sets `activated=0`, row not actually deleted ✅
- [x] Test: delete user → trigger deactivates user AND all child accounts ✅
- [x] Test: create user / create account / FK — covered by all tests above ✅
- [x] Test: overdraft CHECK constraint — covered by insufficient funds test ✅

---

## LAYER 3 — `models/models.py`

- [x] `UserCreate` — name (min_length=1)
- [x] `UserResponse` — id, name, activated
- [x] `BankCreate` — name (min_length=1)
- [x] `BankResponse` — id, name
- [x] `AccountCreate` — user_id, bank_id, account_type, balance
- [x] `AccountResponse` — all account fields safe to expose
- [x] `TransactionCreate` — from_id, to_id, amount
- [x] `TransactionResponse` — id, from_id, to_id, amount, transaction_time
- [x] Validator: amount must be > 0
- [x] Validator: account_type — `Literal['Savings', 'Business', 'Current', 'Fixed Deposit', 'Salary']`
- [x] Validator: balance must be ≥ 0
- [x] `model_config = ConfigDict(from_attributes=True)` on all base models
- [x] `field_validator` on Create models only — no double-conversion bug
- [x] `field_serializer` paise → rupees on output
- [x] rupees → paise on input via validator

---

## LAYER 4 — `models/test_models.py`

- [x] Test: `UserCreate` rejects empty name ✅
- [x] Test: `TransactionCreate` rejects amount ≤ 0 ✅
- [x] Test: `AccountCreate` rejects negative balance ✅
- [x] Test: balance converts rupees → paise correctly on input ✅
- [x] Test: balance converts paise → rupees correctly on output ✅
- [x] Test: `UserResponse` serialises from ORM object — skipped, covered by routes ✅
- [x] Test: `AccountCreate` rejects invalid account_type — not written yet ⚠️

---

## LAYER 5 — `app.py`

- [x] FastAPI app initialised
- [x] `get_db` dependency wired in
- [x] `GET /` → redirects to `/docs`

**Users**
- [x] `POST   /users`
- [x] `GET    /users/{id}`
- [x] `DELETE /users/{id}` — soft delete via trigger ✅ confirmed working
- [x] `GET    /users/{user_id}/accounts`

**Banks**
- [x] `GET    /banks`
- [x] `GET    /banks/{id}`
- [x] `POST   /banks`
- [x] `GET    /banks/{id}/accounts`

**Accounts**
- [x] `POST   /accounts`
- [x] `GET    /accounts/{id}`
- [x] `DELETE /accounts/{id}` — soft delete via trigger ✅ confirmed working
- [x] `GET    /accounts/{id}/transactions`

**Transactions**
- [x] `POST   /transactions` — trigger handles balance updates
- [x] `GET    /transactions/{id}`
- [x] `IntegrityError` caught → returns 400 with trigger message

**Error handling**
- [x] All routes use `response_model=`
- [x] 404 on missing resources
- [x] 400 on trigger abort (insufficient funds, inactive account)
- [x] `GET /users/{id}` — currently returns user only, not accounts ⚠️ minor

---

## LAYER 6 — Integration Tests

- [x] Skipped — trigger tests in Layer 2 + live Render deployment cover this adequately for v1

---

## LAYER 7 — Deployment

- [x] Deploy to Render — Singapore region ✅
- [x] Live URL: https://rbi-fastapi.onrender.com
- [x] `/` redirects to `/docs` ✅
- [x] Auto-deploys on `git push` to main ✅
- [ ] `README.md` written — setup instructions, env vars, how to run, live URL
- [ ] `pyproject.toml` has no stdlib packages (`re`, `sqlite3`)
- [ ] Live URL added to resume

---

## ⚠️ Critical Reminders

> Read before writing any code.

1. **Trigger owns balance updates.** Never update balances in SQLAlchemy — double-update bug.

2. **`PRAGMA foreign_keys = ON` per connection.** Set via SQLAlchemy event listener in `db.py`.

3. **Tests use in-memory DB only.** Never touch `rbi.db` in tests.

4. **Flush before FK children.** Always `db.flush()` after parent rows before inserting children.

5. **Validators on Create only.** `field_validator` on XCreate, never XBase — response models read raw paise.

6. **Re-query after rollback or trigger DELETE.** Objects are detached — never refresh, always re-query by ID.

7. **Savepoint fixture.** `begin_nested()` in `db` fixture rolls back even committed data between tests.