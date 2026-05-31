import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE_URL = os.environ.get("DATABASE_URL")

ORACLE_USER = os.environ.get("ORACLE_USER", "system")
ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "1998")
ORACLE_HOST = os.environ.get("ORACLE_HOST", "localhost")
ORACLE_PORT = os.environ.get("ORACLE_PORT", "1521")
ORACLE_SERVICE_NAME = os.environ.get("ORACLE_SERVICE_NAME", "XEPDB1")

# Default connection string (senin ekran görüntüne göre)
DEFAULT_ORACLE_DSN = f"{ORACLE_HOST}:{ORACLE_PORT}/?service_name={ORACLE_SERVICE_NAME}"

if DATABASE_URL:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

else:
    SQLALCHEMY_DATABASE_URI = (
        f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{DEFAULT_ORACLE_DSN}"
    )

SQLALCHEMY_DATABASE_TRACK_MODIFICATIONS = False
USE_ORACLE = SQLALCHEMY_DATABASE_URI.startswith("oracle")

ALLOWED_EXTENSIONS = {"csv", "xlsx"}
APPLICATION_TYPES = [("BIPortal", "BIPortal")]
UPLOAD_TYPES = [
    ("NORMAL", "Normal Yükleme"),
    ("FAST", "Hızlı Yükleme"),
]
SAMPLE_CSV_NAME = "AdslUplTempl.xlsx"