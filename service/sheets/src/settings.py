
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


ROOTDIR = Path(__file__).parent.parent.parent.parent
SERVICE_DIR = Path(__file__).parent.parent

LOGS_DIR = SERVICE_DIR / "data/logs/"
os.makedirs(LOGS_DIR, exist_ok=True)

DEBUG = os.getenv("DEBUG").lower() in ("true", "1", "t", "on")
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(name)s | %(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "main_logs.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
    force=True,
)
logger = logging.getLogger()

logging.getLogger("asyncio").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)

get_env = os.getenv("GOOGLE_SH_CREDS")
if get_env:
    try:
        GOOGLE_SH_CREDS: dict = json.loads(get_env)
    except json.JSONDecodeError:
        logger.exception("Invalid GOOGLE_SH_CREDS format.")
    except Exception as e:
        logger.exception(f"Error initializing GOOGLE_SH_CREDS: {e}")
