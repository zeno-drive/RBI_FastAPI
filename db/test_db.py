import pytest
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from db.db import Base, User, Account, Bank, Transaction

TEST_DB = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    from sqlalchemy import event

    eng = create_engine("sqlite:///:memory:")

    # enforce FK on every connection
    @event.listens_for(eng, "connect")
    def set_fk(conn, _):
        conn.execute("PRAGMA foreign_keys = ON")

    # load schema through the same engine
    with eng.connect() as conn:
        with open("schema.sql") as f:
            conn.connection.executescript(f.read())
    return eng


@pytest.fixture(scope="function")
def db(engine):
    connection = engine.connect()
    transaction = connection.begin_nested()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def test_transaction_updates_balances(db):
    bank = Bank(id=9000, name="TestBank")
    user = User(id=8000, name="TestUser")
    db.add_all([bank, user])
    db.flush()

    acc1 = Account(
        id=7000, user_id=8000, bank_id=9000, account_type="Savings", balance=50000
    )
    acc2 = Account(
        id=7001, user_id=8000, bank_id=9000, account_type="Savings", balance=10000
    )
    db.add_all([acc1, acc2])
    db.flush()
    txn = Transaction(from_id=7000, to_id=7001, amount=5000)
    db.add(txn)
    db.commit()

    # assert
    db.refresh(acc1)
    db.refresh(acc2)
    assert acc1.balance == 45000
    assert acc2.balance == 15000


def test_transaction_fails_for_lowbalance(db):
    bank = Bank(id=9000, name="TestBank")
    user = User(id=8000, name="TestUser")
    db.add_all([bank, user])
    db.flush()

    acc1 = Account(
        id=7000, user_id=8000, bank_id=9000, account_type="Savings", balance=100
    )
    acc2 = Account(
        id=7001, user_id=8000, bank_id=9000, account_type="Savings", balance=10000
    )
    db.add_all([acc1, acc2])
    db.commit()

    with pytest.raises(IntegrityError):
        txn = Transaction(from_id=7000, to_id=7001, amount=5000)
        db.add(txn)
        db.commit()

    db.rollback()

    acc1 = db.query(Account).filter(Account.id == 7000).first()
    acc2 = db.query(Account).filter(Account.id == 7001).first()
    assert acc1.balance == 100
    assert acc2.balance == 10000


def test_transaction_fails_for_deactivated_account(db):
    bank = Bank(id=9000, name="TestBank")
    user = User(id=8000, name="TestUser")
    db.add_all([bank, user])
    db.flush()

    acc1 = Account(
        id=7000,
        user_id=8000,
        bank_id=9000,
        activated=0,
        account_type="Savings",
        balance=100,
    )
    acc2 = Account(
        id=7001, user_id=8000, bank_id=9000, account_type="Savings", balance=10000
    )
    db.add_all([acc1, acc2])
    db.commit()

    with pytest.raises(IntegrityError):
        txn = Transaction(from_id=7000, to_id=7001, amount=5000)
        db.add(txn)
        db.commit()

    db.rollback()


def test_soft_deletion_account(db):
    bank = Bank(id=9000, name="TestBank")
    user = User(id=8000, name="TestUser")
    db.add_all([bank, user])
    db.flush()

    acc1 = Account(
        id=7000, user_id=8000, bank_id=9000, account_type="Savings", balance=100
    )
    db.add(acc1)
    db.commit()

    db.delete(acc1)
    db.commit()

    result = db.query(Account).filter(Account.id == 7000).first()
    assert result is not None
    assert result.activated == 0


def test_soft_deletion_user(db):
    bank = Bank(id=9000, name="TestBank")
    user = User(id=8000, name="TestUser")
    db.add_all([bank, user])
    db.flush()

    acc1 = Account(
        id=7000, user_id=8000, bank_id=9000, account_type="Savings", balance=100
    )
    acc2 = Account(
        id=7001, user_id=8000, bank_id=9000, account_type="Current", balance=100
    )
    acc3 = Account(
        id=7002, user_id=8000, bank_id=9000, account_type="Salary", balance=100
    )
    db.add(acc1)
    db.add(acc2)
    db.add(acc3)
    db.commit()

    db.delete(user)
    db.commit()

    result = db.query(Account).filter(Account.user_id == 8000).all()

    assert len(result) == 3
    assert result[0].activated == 0
    assert result[1].activated == 0
    assert result[2].activated == 0
