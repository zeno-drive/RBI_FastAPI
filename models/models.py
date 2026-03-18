from pydantic import BaseModel, ConfigDict, field_serializer


def paise_to_rupees(v: int) -> float:
    return round(v / 100, 2)


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str

class BankBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str

class AccountBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    bank_id: int
    account_type: str
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


class UserCreate(UserBase): pass
class BankCreate(BankBase): pass
class AccountCreate(AccountBase): pass
class TransactionCreate(TransactionBase): pass

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