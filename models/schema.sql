CREATE TABLE IF NOT EXISTS 'users'(
    'id' INTEGER PRIMARY KEY,
    'name' TEXT NOT NULL
    'activated' TEXT CHECK(activated==1 or activated==0) DEFAULT 1
    'created_at' NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP 
)

CREATE TABLE IF NOT EXISTS 'banks'(
    'id' INTEGER PRIMARY KEY,
    'name' TEXT NOT NULL

) 
CREATE TABLE IF NOT EXISTS 'accounts'(
    'id' INTEGER PRIMARY KEY,
    'user_id' INTEGER,
    'bank_id' INTEGER,
    'activated' INTEGER CHECK(activated==1 or activated==0) DEFAULT 1,
    'created_at' NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY('user_id' REFERENCES 'user'('id'),
    'bank_id' REFERENCES 'banks'('id') )
)

CREATE TABLE IF NOT EXISTS 'transaction_history'(
    'id' INTEGER PRIMARY KEY AUTO_INCREMENT,
    'from_id' INTEGER NOT NULL,
    'to_id' INTEGER NOT NULL,
    'transaction_time' NUMERIC DEFAULT CURRENT_TIMESTAMP
)