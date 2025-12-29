import re
from model import create_transaction

def parse_voice_text(text: str):
    """
    Supported formats (for now):
    - "spent 450 on swiggy"
    - "paid 199 for netflix"
    """

    text = text.lower()

    patterns = [
        r"spent\s+(\d+)\s+on\s+(.+)",
        r"paid\s+(\d+)\s+for\s+(.+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            description = match.group(2).title()

            return create_transaction(
                description=description,
                amount=-amount,
                category="Other",
                account="UPI",
                source="voice"
            )

    return None
