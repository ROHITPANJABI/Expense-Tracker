import pandas as pd
from datetime import date

COLUMNS = ["date", "description", "amount", "account", "category", "source"]

def create_transaction(
    description: str,
    amount: float,
    account: str = "HDFC",
    category: str = "Other",
    source: str = "manual",
    txn_date: str | None = None
) -> pd.DataFrame:
    """
    Returns a ONE-ROW dataframe matching the locked schema
    """
    if txn_date is None:
        txn_date = date.today().isoformat()

    data = [[txn_date, description, amount, account, category, source]]
    return pd.DataFrame(data, columns=COLUMNS)

