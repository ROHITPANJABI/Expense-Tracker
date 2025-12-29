import json
import openai
import streamlit as st
from model import create_transaction

openai.api_key = st.secrets["OPENAI_API_KEY"]

SYSTEM_PROMPT = """
You are an expense extraction assistant.

From a user sentence, extract:
- amount (number, no currency symbols)
- description (short noun phrase)
- category (Food, Transport, Shopping, Entertainment, Rent, Income, Other)
- account (Cash, UPI, Credit Card, Bank)

Rules:
- If unclear, guess best option
- Return ONLY valid JSON
"""

def parse_voice_text_ai(text: str):
    if not text:
        return None

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.1
    )

    try:
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

    except Exception:
        return None
