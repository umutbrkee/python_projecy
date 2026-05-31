from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import USE_ORACLE

db = SQLAlchemy()


def _ensure_sqlite_columns(engine):
    with engine.connect() as conn:
        table = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='DP_APPL_XLS_UPLOAD.XU_UPLOAD'"))
        if table.fetchone() is None:
            return

        result = conn.execute(text("PRAGMA table_info('XU_UPLOAD')"))
        existing = {row[1].upper() for row in result.fetchall()}

        # Eğer eski tablo yapısı varsa, yeniden oluşturmak için temizleyelim.
        old_columns = {"UPLOAD_ID", "APPLICATION_TYPE", "UPLOAD_TYPE", "FILE_NAME", "CREATED_BY", "CREATED_AT"}
        if old_columns.intersection(existing) or "ID" in existing and "TICKETNO" not in existing:
            conn.execute(text("DROP TABLE IF EXISTS XU_UPLOAD"))
            conn.execute(text("DROP TABLE IF EXISTS XU_UPLOADDATA_V2"))


def init_db(app):
    if USE_ORACLE:
        return

    with app.app_context():
        engine = db.engine
        _ensure_sqlite_columns(engine)
        db.create_all()
