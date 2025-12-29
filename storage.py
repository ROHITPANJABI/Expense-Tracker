import sqlite3
import pandas as pd

DB_PATH = "expenses.db"
TABLE_NAME = "transactions"

COLUMNS = [
    "date",
    "amount",
    "category",
    "account",
    "description",
    "source"
]

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            date TEXT,
            amount REAL,
            category TEXT,
            account TEXT,
            description TEXT,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_transactions(df: pd.DataFrame):
    conn = get_connection()
    df[COLUMNS].to_sql(TABLE_NAME, conn, if_exists="append", index=False)
    conn.close()

def load_transactions() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    return df
