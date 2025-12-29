import streamlit as st
from model import create_transaction
from storage import init_db, insert_transactions, load_transactions
from voice_parser import parse_voice_text
import streamlit as st

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Private Expense Tracker")

        password = st.text_input(
            "Enter password",
            type="password"
        )

        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.stop()

check_password()
# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Expense Tracker",
    layout="centered"
)

st.title("💸 Expense Tracker")

# ---------------- INIT DB ----------------
init_db()

# ---------------- MANUAL ENTRY ----------------
st.subheader("➕ Manual Entry")

with st.form("manual_form"):
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    category = st.selectbox(
        "Category",
        ["Food", "Transport", "Rent", "Shopping", "Entertainment", "Income", "Other"]
    )
    account = st.selectbox(
        "Paid Using",
        ["Cash", "UPI", "HDFC_CC", "HDFC", "Other"]
    )

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

# ---------------- VOICE ENTRY (KEYBOARD MIC) ----------------
st.divider()
st.subheader("🎤 Voice Entry")
st.caption("Tap the text box → use your keyboard mic 🎙️ → speak naturally")

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

voice_text = st.text_input(
    "Example: Spent 450 on Swiggy | Paid 199 for Netflix",
    value=st.session_state.voice_text
)

if voice_text:
    df_voice = parse_voice_text(voice_text)

    if df_voice is not None:
        st.subheader("👀 Preview (Editable)")
        edited_df = st.data_editor(df_voice, num_rows="fixed")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Save Voice Entry"):
                insert_transactions(edited_df)
                st.session_state.voice_text = ""
                st.success("Voice entry saved!")

        with col2:
            if st.button("❌ Discard"):
                st.session_state.voice_text = ""
                st.warning("Voice entry discarded")
    else:
        st.error("Could not understand. Try: 'Spent 450 on Swiggy'")

# ---------------- ALL TRANSACTIONS ----------------
st.divider()
st.subheader("📄 All Transactions")

df_all = load_transactions()

if not df_all.empty:
    st.dataframe(df_all.sort_values("date", ascending=False))
else:
    st.info("No transactions yet.")
