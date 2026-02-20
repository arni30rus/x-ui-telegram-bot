import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS_ID = list(map(int, os.getenv("ADMINS_ID").split(",")))

XUI_BASE_URL = os.getenv("XUI_BASE_URL")
XUI_USERNAME = os.getenv("XUI_USERNAME")
XUI_PASSWORD = os.getenv("XUI_PASSWORD")
XUI_INBOUND_ID = int(os.getenv("XUI_INBOUND_ID", 1))
XUI_DB_PATH = os.getenv("XUI_DB_PATH", "/etc/x-ui/x-ui.db")


SERVER_DOMAIN = os.getenv("SERVER_DOMAIN")
SHARED_SID = os.getenv("SHARED_SID")

REALITY_PUBLIC_KEY = os.getenv("REALITY_PUBLIC_KEY")
REALITY_SNI = os.getenv("REALITY_SNI")
REALITY_SPIDER_X = os.getenv("REALITY_SPIDER_X", "")
REALITY_FINGERPRINT = os.getenv("REALITY_FINGERPRINT", "chrome")
