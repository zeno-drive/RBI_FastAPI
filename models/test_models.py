import pytest
from pydantic import ValidationError
from models.models import *


def test_user_create_rejects_empty_name():
    with pytest.raises(ValidationError):
        UserCreate(name="")


def test_user_create_valid():
    user = UserCreate(name="Zeno")
    assert user.name == "Zeno"


def test_acc_balance_gte_zero():
    with pytest.raises(ValidationError):
        AccountCreate(user_id=8000, bank_id=9000, account_type="Savings", balance=-1)


def test_transaction_amount_gt_zero():
    with pytest.raises(ValidationError):
        TransactionCreate(from_id=7000, to_id=7001, amount=0)


def test_rupees_to_paise():
    value = rupees_to_paise(10)
    assert value == 1000


def test_paise_to_rupees():
    value = paise_to_rupees(100)
    assert value == 1
