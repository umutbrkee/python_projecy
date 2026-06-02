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

# ===== LDAP / Active Directory Konfigürasyonu =====
# Örnek: LDAP_SERVER=dc.ttnet.local
LDAP_ENABLED = os.environ.get("LDAP_ENABLED", "False").lower() == "true"
LDAP_SERVER = os.environ.get("LDAP_SERVER", "localhost")
LDAP_PORT = int(os.environ.get("LDAP_PORT", "389"))
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "dc=ttnet,dc=local")
LDAP_USE_SSL = os.environ.get("LDAP_USE_SSL", "False").lower() == "true"
LDAP_TIMEOUT = int(os.environ.get("LDAP_TIMEOUT", "10"))

# İzin verilen AD grupları (virgülle ayrılmış)
# Örnek: TTNET\DWH_ADMINS_BO,TTNET\BO_Upload_Users
LDAP_ALLOWED_GROUPS = [
    g.strip() for g in os.environ.get(
        "LDAP_ALLOWED_GROUPS",
        "TTNET\\DWH_ADMINS_BO,TTNET\\BO_Upload_Users"
    ).split(",")
]

ALLOWED_EXTENSIONS = {"csv", "xlsx"}
APPLICATION_TYPES = [("BIPortal", "BIPortal")]
UPLOAD_TYPES = [
    ("NORMAL", "Normal Yükleme"),
    ("FAST", "Hızlı Yükleme"),
]
SAMPLE_CSV_NAME = "AdslUplTempl.xlsx"