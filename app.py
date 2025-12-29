import streamlit as st
from model import create_transaction
from storage import init_db, insert_transactions, load_transactions
from ai_voice_parser import parse_voice_text_ai as parse_voice_text

# =========================================================
# 🔐 PASSWORD PROTECTION
# =========================================================
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Private Expense Tracker")
        password = st.text_input("Enter password", type="password")

        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.stop()

check_password()

# =========================================================
# ⚙️ CONFIG
# =========================================================
st.set_page_config(page_title="Expense Tracker", layout="centered")
st.title("💸 Expense Tracker")

CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Shopping",
    "Entertainment",
    "Income",
    "Other"
]

ACCOUNTS = [
    "Cash",
    "UPI",
    "HDFC_CC",
    "HDFC",
    "Other"
]

# =========================================================
# 🗄️ INIT DATABASE
# =========================================================
init_db()

# =========================================================
# ➕ MANUAL ENTRY
# =========================================================
st.subheader("➕ Manual Entry")

with st.form("manual_form"):
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    category = st.selectbox("Category", CATEGORIES)
    account = st.selectbox("Paid Using", ACCOUNTS)
    submitted = st.form_submit_button("Preview")

if submitted:
    df_manual = create_transaction(
        description=description,
        amount=amount if category == "Income" else -abs(amount),
        category=category,
        account=account,
        source="manual"
    )

    st.subheader("👀 Preview")
    st.dataframe(df_manual)

    if st.button("✅ Save Manual Entry"):
        insert_transactions(df_manual)
        st.success("Manual entry saved!")

# =========================================================
# 🎤 VOICE ENTRY (KEYBOARD MIC + AI PARSER)
# =========================================================
st.divider()
st.subheader("🎤 Voice Entry")
st.caption("Tap the text box → use your keyboard mic 🎙️ → speak naturally")

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

voice_text = st.text_input(
    "Example: Spent 2000 on TV using credit card",
    key="voice_text"
)

if st.session_state.voice_text:
    parsed_df = parse_voice_text(st.session_state.voice_text)

    if parsed_df is not None:
        st.subheader("👀 Review Voice Entry")

        row = parsed_df.iloc[0]

        category = st.selectbox(
            "Category",
            CATEGORIES,
            index=CATEGORIES.index(row["category"])
            if row["category"] in CATEGORIES else CATEGORIES.index("Other"),
            key="voice_category"
        )

        account = st.selectbox(
            "Paid Using",
            ACCOUNTS,
            index=ACCOUNTS.index(row["account"])
            if row["account"] in ACCOUNTS else ACCOUNTS.index("UPI"),
            key="voice_account"
        )

        parsed_df.loc[0, "category"] = category
        parsed_df.loc[0, "account"] = account

        st.subheader("📄 Final Preview")
        st.dataframe(parsed_df)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Save Voice Entry"):
                insert_transactions(parsed_df)
                st.session_state.voice_text = ""
                st.success("Voice entry saved!")

        with col2:
            if st.button("❌ Discard"):
                st.session_state.voice_text = ""
                st.warning("Voice entry discarded")
    else:
        st.error("Could not understand the sentence. Try again.")

# =========================================================
# 📄 ALL TRANSACTIONS
# =========================================================
st.divider()
st.subheader("📄 All Transactions")

df_all = load_transactions()

if not df_all.empty:
    st.dataframe(df_all.sort_values("date", ascending=False))
else:
    st.info("No transactions yet.")
