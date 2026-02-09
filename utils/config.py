import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5032"))
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
THREAD = int(os.getenv("THREAD", "1"))
PAGE_COUNT = int(os.getenv("PAGE_COUNT", "1"))
PROXY_SUPPORT = os.getenv("PROXY_SUPPORT", "false").lower() == "true"
CLEANUP_INTERVAL_MINUTES = int(os.getenv("CLEANUP_INTERVAL_MINUTES", "60"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOG_ROTATION = os.getenv("LOG_ROTATION", "10 MB")
LOG_RETENTION = os.getenv("LOG_RETENTION", "7 days")
STATIC_DIR = BASE_DIR / "static"
LOGS_DIR = BASE_DIR / "logs"