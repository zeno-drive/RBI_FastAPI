from db.db import *
from fastapi import FastAPI, Depends, HTTPException
from models.models import *
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

app = FastAPI()

# users
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.delete("/users/{user_id}", response_model=UserResponse)
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return db.query(User).filter(User.id == user_id).first()

# accounts
@app.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.post("/accounts", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    new_account = Account(**account.model_dump())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

@app.delete("/accounts/{account_id}", response_model=AccountResponse)
def deactivate_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return db.query(Account).filter(Account.id == account_id).first()


# banks
@app.get("/banks/{bank_id}", response_model=BankResponse)
def get_bank(bank_id: int, db: Session = Depends(get_db)):
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    return bank

@app.post("/banks", response_model=BankResponse)
def create_bank(bank: BankCreate, db: Session = Depends(get_db)):
    new_bank = Bank(**bank.model_dump())
    db.add(new_bank)
    db.commit()
    db.refresh(new_bank)
    return new_bank

# transactions
@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.post("/transactions", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    try:   
        new_transaction = Transaction(**transaction.model_dump())
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e.orig))

@app.get("/accounts/{account_id}/transactions",response_model=List[TransactionResponse])
def account_transaction_history(account_id:int,db:Session=Depends(get_db)):
    transaction=db.query(Transaction).filter(or_(Transaction.from_id==account_id,Transaction.to_id==account_id)).all()
    if not transaction:
        return []
    return transaction 
#banks
@app.get("/banks", response_model=List[BankResponse])
def get_all_banks(db: Session = Depends(get_db)):
    return db.query(Bank).all()

@app.get("/banks/{bank_id}/accounts",response_model=List[AccountResponse])
def accounts_in_bank(bank_id:int,db:Session=Depends(get_db)):
    accounts=db.query(Account).filter(Account.bank_id==bank_id).all()
    if not accounts:
        return []
    return accounts

    