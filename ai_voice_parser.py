import json
import openai
import streamlit as st
from model import create_transaction

# ---------------------------------------------------------
# SYSTEM PROMPT (MUST EXIST BEFORE USE)
# ---------------------------------------------------------
SYSTEM_PROMPT = """
You are an expense extraction assistant.

From a user sentence, extract:
- amount (number, no currency symbols)
- description (short noun phrase)
- category (Food, Transport, Shopping, Entertainment, Rent, Income, Other)
- account (Cash, UPI, Credit Card, Bank)

Return ONLY valid JSON.
"""

def parse_voice_text_ai(text: str):
    if not text:
        return None

    # Read secret ONLY at runtime
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("OPENAI_API_KEY not found in secrets")
        return None

    openai.api_key = st.secrets["OPENAI_API_KEY"]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )

        data = json.loads(response.choices[0].message.content)

        amount = float(data["amount"])
        description = data["description"].title()
        category = data.get("category", "Other")
        account = data.get("account", "UPI")

        return create_transaction(
            description=description,
            amount=-abs(amount),
            category=category,
            account=account,
            source="voice"
        )

    except Exception as e:
        st.error(f"AI parsing failed: {e}")
        return None
