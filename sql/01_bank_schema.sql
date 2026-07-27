CREATE SCHEMA bank;

CREATE TABLE bank.customers (
  customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  ssn_last4 CHAR(4) NOT NULL,          -- PII you'll mask later in Spark
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE bank.accounts (
  account_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id BIGINT REFERENCES bank.customers,
  account_type TEXT CHECK (account_type IN ('CHECKING','SAVINGS','CREDIT')),
  balance NUMERIC(14,2) NOT NULL DEFAULT 0,
  status TEXT DEFAULT 'ACTIVE',
  opened_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE bank.merchants (
  merchant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,              -- 'GROCERY','TRAVEL','GAS', etc.
  country CHAR(2) DEFAULT 'US'
);

CREATE TABLE bank.transactions (
  txn_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id BIGINT REFERENCES bank.accounts,
  merchant_id BIGINT REFERENCES bank.merchants,
  amount NUMERIC(12,2) NOT NULL,
  currency CHAR(3) DEFAULT 'USD',
  txn_type TEXT CHECK (txn_type IN ('PURCHASE','REFUND','TRANSFER','ATM')),
  status TEXT DEFAULT 'POSTED',        -- 'PENDING','POSTED','DECLINED'
  txn_ts TIMESTAMPTZ NOT NULL DEFAULT now()
);