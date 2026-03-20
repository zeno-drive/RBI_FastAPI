from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, Field
from typing import Literal
from datetime import datetime


def paise_to_rupees(v: int) -> float:
    return round(v / 100, 2)


def rupees_to_paise(v) -> int:
    return round(float(v) * 100)


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(min_length=1)


class BankBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(min_length=1)


class AccountBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    bank_id: int
    account_type: Literal["Savings", "Business", "Current", "Fixed Deposit", "Salary"]
    balance: int

    @field_serializer("balance")
    def serialize_balance(self, v) -> float:
        return paise_to_rupees(v)


class TransactionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    from_id: int
    to_id: int
    amount: int

    @field_serializer("amount")
    def serialize_amount(self, v) -> float:
        return paise_to_rupees(v)


class UserCreate(UserBase):
    pass


class BankCreate(BankBase):
    pass


class AccountCreate(AccountBase):
    @field_validator("balance", mode="before")
    @classmethod
    def convert_balance(cls, v) -> int:
        if float(v) < 0:
            raise ValueError("balance cannot be negative")
        return rupees_to_paise(v)


class TransactionCreate(TransactionBase):
    @field_validator("amount", mode="before")
    @classmethod
    def convert_amount(cls, v) -> int:
        if v <= 0:
            raise ValueError("Transfer amount must be greater than zero")
        return rupees_to_paise(v)


class UserResponse(UserBase):
    id: int
    activated: bool


class BankResponse(BankBase):
    id: int


class AccountResponse(AccountBase):
    id: int
    activated: bool


class TransactionResponse(TransactionBase):
    id: int
    transaction_time: datetime
