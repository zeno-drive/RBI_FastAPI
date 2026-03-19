import pytest
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.db import Base, User, Account, Bank, Transaction


TEST_DB = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db(engine):
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.rollback()   
    session.close()

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

def test_transaction_updates_balances(db):
    # insert parents first, flush to DB before adding children
    bank = Bank(id=9000, name="TestBank")
    user = User(id=8000, name="TestUser")
    db.add_all([bank, user])
    db.flush()                    # ← write bank + user to DB first

    acc1 = Account(id=7000, user_id=8000, bank_id=9000,
                   account_type="Savings", balance=50000)
    acc2 = Account(id=7001, user_id=8000, bank_id=9000,
                   account_type="Savings", balance=10000)
    db.add_all([acc1, acc2])
    db.flush()                    # ← write accounts before transaction

    # act — trigger fires here
    txn = Transaction(from_id=7000, to_id=7001, amount=5000)
    db.add(txn)
    db.commit()

    # assert
    db.refresh(acc1)
    db.refresh(acc2)
    assert acc1.balance == 45000
    assert acc2.balance == 15000