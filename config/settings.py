from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SESSION_TIMEOUT_SECONDS = int(os.getenv("MADHU_SESSION_TIMEOUT_SECONDS", "900"))
LOGIN_MAX_FAILURES = int(os.getenv("MADHU_LOGIN_MAX_FAILURES", "5"))
LOGIN_LOCKOUT_SECONDS = int(os.getenv("MADHU_LOGIN_LOCKOUT_SECONDS", "300"))

# Educational simulation limits, not real banking limits.
MAX_TRANSFER_PER_TRANSACTION_MINOR = int(os.getenv("MADHU_MAX_TRANSFER_MINOR", "100000"))
MAX_DAILY_TRANSFER_MINOR = int(os.getenv("MADHU_DAILY_TRANSFER_MINOR", "100000"))
MAX_DAILY_TRANSFER_COUNT = int(os.getenv("MADHU_DAILY_TRANSFER_COUNT", "20"))

CURRENCY = os.getenv("MADHU_CURRENCY", "INR")
ENVIRONMENT = os.getenv("MADHU_ENVIRONMENT", "local")

SMTP_HOST = os.getenv("MADHU_BANK_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("MADHU_BANK_SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("MADHU_BANK_SMTP_USERNAME", "").strip()
# Google displays App Passwords in groups of four characters. Remove spaces so
# users can paste either the grouped or compact form into .env.
SMTP_PASSWORD = os.getenv("MADHU_BANK_SMTP_PASSWORD", "").replace(" ", "").strip()
SMTP_FROM = os.getenv("MADHU_BANK_SMTP_FROM", SMTP_USERNAME).strip()

SMTP_CONFIGURATION_ERROR = ""
if not SMTP_USERNAME or not SMTP_PASSWORD:
	SMTP_CONFIGURATION_ERROR = "Gmail SMTP username and App Password are required."
elif SMTP_USERNAME == "your_email@gmail.com":
	SMTP_CONFIGURATION_ERROR = "Set MADHU_BANK_SMTP_USERNAME to the Gmail address used for sending OTPs."
elif SMTP_PASSWORD == "YOUR_16_CHAR_GMAIL_APP_PASSWORD":
	SMTP_CONFIGURATION_ERROR = "Set MADHU_BANK_SMTP_PASSWORD to a real 16-character Gmail App Password."

ADMIN_USERNAME = os.getenv("MADHU_BANK_ADMIN_USERNAME", "admin").strip()
ADMIN_PASSWORD = os.getenv("MADHU_BANK_ADMIN_PASSWORD", "admin123")
ADMIN_EMAIL = os.getenv(
    "MADHU_BANK_ADMIN_EMAIL",
    SMTP_USERNAME or "admin@madhubank.com"
).strip().lower()
