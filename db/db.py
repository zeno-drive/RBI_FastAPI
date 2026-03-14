from sqlalchemy import create_engine, ForeignKey,func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

engine = create_engine("sqlite:///rbi.db", echo=True)

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

class TransactionHistory(Base):
    __tablename__ = "transaction_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    from_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    to_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    amount: Mapped[int]
    transaction_time: Mapped[datetime] = mapped_column(server_default=func.now())