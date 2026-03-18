from sqlalchemy import create_engine, ForeignKey, func, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker
from datetime import datetime
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "rbi.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)


# enforce FK constraints per connection — SQLite doesn't do this by default
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys = ON")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    with open("schema.sql", "r") as f:
        sql = f.read()
    conn = sqlite3.connect("rbi.db")
    conn.executescript(sql)
    conn.close()


if not DB_PATH.exists():
    init_db()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    activated: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Bank(Base):
    __tablename__ = "banks"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bank_id: Mapped[int] = mapped_column(ForeignKey("banks.id"))
    account_type: Mapped[int]
    balance: Mapped[int]
    activated: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Transaction(Base):
    __tablename__ = "transaction_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    from_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    to_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    amount: Mapped[int]
    transaction_time: Mapped[datetime] = mapped_column(server_default=func.now())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
