import os
import oracledb
from urllib.parse import unquote, urlparse, parse_qs
from config import (
    DATABASE_URL,
    ORACLE_USER,
    ORACLE_PASSWORD,
    ORACLE_DSN,
    ORACLE_HOST,
    ORACLE_PORT,
    ORACLE_SERVICE_NAME,
    ORACLE_SID,
)


def _parse_oracle_url(url):
    parsed = urlparse(url)
    if not parsed.scheme.startswith("oracle"):
        return None

    user = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None
    host = parsed.hostname
    port = parsed.port
    query = parse_qs(parsed.query)
    service_name = query.get("service_name", [None])[0]
    sid = query.get("sid", [None])[0]
    dsn = None
    if host and port and service_name:
        dsn = oracledb.makedsn(host, port, service_name=service_name)
    elif host and port and sid:
        dsn = oracledb.makedsn(host, port, sid=sid)
    elif parsed.path:
        dsn = parsed.path.lstrip("/")
    return user, password, dsn


def get_oracle_connection():
    user = ORACLE_USER
    password = ORACLE_PASSWORD
    dsn = ORACLE_DSN

    if not all([user, password, dsn]) and DATABASE_URL:
        parsed = _parse_oracle_url(DATABASE_URL)
        if parsed is not None:
            user, password, dsn = parsed

    if not all([user, password, dsn]) and ORACLE_USER and ORACLE_PASSWORD and ORACLE_HOST and ORACLE_PORT:
        if ORACLE_SERVICE_NAME:
            dsn = oracledb.makedsn(ORACLE_HOST, int(ORACLE_PORT), service_name=ORACLE_SERVICE_NAME)
        elif ORACLE_SID:
            dsn = oracledb.makedsn(ORACLE_HOST, int(ORACLE_PORT), sid=ORACLE_SID)

    if not all([user, password, dsn]):
        raise RuntimeError(
            "Oracle bağlantısı için ORACLE_USER, ORACLE_PASSWORD ve ORACLE_DSN veya ORACLE_HOST/ORACLE_PORT/ORACLE_SERVICE_NAME/ORACLE_SID ayarlanmalıdır."
        )

    return oracledb.connect(user=user, password=password, dsn=dsn)


def validate_oracle_connection():
    conn = get_oracle_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")
            return cursor.fetchone()[0] == 1
    finally:
        conn.close()
