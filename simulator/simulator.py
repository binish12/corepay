import random
import time
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

conn = psycopg2.connect(
    host="localhost", port=5433,
    dbname="corebank", user="bankadmin", password="bankpass"
)
conn.autocommit = False

CATEGORIES = ["GROCERY", "TRAVEL", "GAS",
              "RESTAURANT", "ONLINE", "UTILITIES", "ATM_NETWORK"]
TXN_TYPES = ["PURCHASE", "REFUND", "TRANSFER", "ATM"]


def seed():
    cur = conn.cursor()

    cur.execute("SELECT count(*) FROM bank.customers")
    if cur.fetchone()[0] > 0:
        print("Already seeded, skipping.")
        return

    # 500 customers
    customers = [
        (fake.name(), fake.unique.email(), str(random.randint(1000, 9999)))
        for _ in range(500)
    ]
    execute_values(
        cur,
        "INSERT INTO bank.customers (full_name, email, ssn_last4) VALUES %s",
        customers,
    )

    cur.execute("SELECT customer_id FROM bank.customers")
    customer_ids = [r[0] for r in cur.fetchall()]

    # ~800 accounts across those customers
    accounts = []
    for _ in range(800):
        cid = random.choice(customer_ids)
        atype = random.choice(["CHECKING", "SAVINGS", "CREDIT"])
        balance = round(random.uniform(50, 20000), 2)
        accounts.append((cid, atype, balance))
    execute_values(
        cur,
        "INSERT INTO bank.accounts (customer_id, account_type, balance) VALUES %s",
        accounts,
    )

    # 100 merchants
    merchants = [
        (fake.company(), random.choice(CATEGORIES), "US") for _ in range(100)
    ]
    execute_values(
        cur,
        "INSERT INTO bank.merchants (name, category, country) VALUES %s",
        merchants,
    )

    conn.commit()
    print("Seeded 500 customers, 800 accounts, 100 merchants.")


def stream():
    cur = conn.cursor()
    cur.execute("SELECT account_id FROM bank.accounts")
    account_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT merchant_id FROM bank.merchants")
    merchant_ids = [r[0] for r in cur.fetchall()]

    print("Streaming transactions... Ctrl+C to stop.")
    while True:
        batch_size = random.randint(5, 20)
        rows = []
        for _ in range(batch_size):
            account_id = random.choice(account_ids)
            merchant_id = random.choice(merchant_ids)
            txn_type = random.choices(TXN_TYPES, weights=[80, 5, 10, 5])[0]

            # 90% small purchase, occasional large transfer
            if txn_type == "TRANSFER":
                amount = round(random.uniform(100, 5000), 2)
            else:
                amount = round(random.uniform(2, 300), 2)

            status = random.choices(
                ["POSTED", "PENDING", "DECLINED"], weights=[90, 8, 2]
            )[0]

            currency = "USD"
            txn_ts = datetime.now()

            # inject ~1% dirty data
            if random.random() < 0.01:
                dirty_choice = random.choice(
                    ["negative_amount", "future_ts", "bad_currency"])
                if dirty_choice == "negative_amount" and txn_type == "PURCHASE":
                    amount = -abs(amount)
                elif dirty_choice == "future_ts":
                    txn_ts = datetime.now() + timedelta(days=30)
                elif dirty_choice == "bad_currency":
                    currency = "XXX"

            rows.append((account_id, merchant_id, amount,
                        currency, txn_type, status, txn_ts))

        execute_values(
            cur,
            """INSERT INTO bank.transactions
               (account_id, merchant_id, amount, currency, txn_type, status, txn_ts)
               VALUES %s""",
            rows,
        )
        conn.commit()
        print(f"Inserted {batch_size} transactions.")
        time.sleep(1)


if __name__ == "__main__":
    seed()
    stream()
