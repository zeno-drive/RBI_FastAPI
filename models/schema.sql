CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    activated INTEGER NOT NULL 
    CHECK(activated==1 or activated==0) DEFAULT 1,
    created_at NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE IF NOT EXISTS banks(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL

);

CREATE TABLE IF NOT EXISTS accounts(
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    bank_id INTEGER NOT NULL,
    account_type INTEGER NOT NULL,
    balance INTEGER NOT NULL CHECK(balance>=0),
    activated INTEGER NOT NULL 
    CHECK(activated==1 or activated==0) DEFAULT 1,
    created_at NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(bank_id) REFERENCES banks(id)
);

CREATE TABLE IF NOT EXISTS transaction_history(
    id INTEGER PRIMARY KEY,
    from_id INTEGER NOT NULL,
    to_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    transaction_time NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(from_id) REFERENCES accounts(id),
    FOREIGN KEY(to_id) REFERENCES accounts(id)
);

CREATE INDEX IF NOT EXISTS  user_index ON users(name);
CREATE INDEX IF NOT EXISTS  bank_index  ON banks(name);
CREATE INDEX IF NOT EXISTS  accounts_index ON accounts(bank_id,user_id);
CREATE INDEX IF NOT EXISTS  transaction_history_index ON transaction_history(from_id,to_id);

CREATE TRIGGER IF NOT EXISTS deactivate_account
BEFORE DELETE ON accounts
FOR EACH ROW
BEGIN
    UPDATE accounts
    SET activated=0
    WHERE id=OLD.id;
    SELECT RAISE(IGNORE);
END;

CREATE TRIGGER IF NOT EXISTS deactivate_user_and_child_accounts
BEFORE DELETE ON users
FOR EACH ROW
BEGIN
    UPDATE users
    SET activated=0
    WHERE id=OLD.id;
    UPDATE accounts
    SET activated=0
    WHERE user_id=OLD.id;
    SELECT RAISE(IGNORE);
END;


CREATE TRIGGER IF NOT EXISTS transactions
BEFORE INSERT ON transaction_history
FOR EACH ROW
BEGIN
    SELECT CASE 
        WHEN(SELECT activated FROM accounts WHERE id=NEW.from_id)=0
            THEN RAISE(ABORT,'ERROR:Sending account not active');
        WHEN(SELECT activated FROM accounts WHERE id=NEW.to_id)=0
            THEN RAISE(ABORT,'ERROR:Reciveing account not active');
        WHEN(SELECT balance FROM accounts WHERE id=NEW.from_id)<NEW.amount
            THEN RAISE(ABORT,'ERROR:Sending account has insufficient funds');
    END;
    UPDATE accounts
    SET balance=balance-NEW.amount
    WHERE id=NEW.from_id;
    
    UPDATE accounts
    SET balance=balance+NEW.amount
    WHERE id=NEW.to_id;
END;



