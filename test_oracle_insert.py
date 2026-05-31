import os
from pathlib import Path

if not any([os.environ.get("DATABASE_URL"), os.environ.get("ORACLE_USER")]):
    raise RuntimeError(
        "Lütfen veritabanı bağlantısı için DATABASE_URL veya ORACLE_USER/ORACLE_PASSWORD/ORACLE_DSN ortam değişkenlerini ayarlayın."
    )

from app import app
from services.upload_service import process_csv_upload

if __name__ == "__main__":
    sample_file = Path(__file__).resolve().parent / "sample_data" / os.environ.get("SAMPLE_CSV_NAME", "AdslUplTempl.xlsx")

    if not sample_file.exists():
        raise FileNotFoundError(f"Örnek dosya bulunamadı: {sample_file}")

    with open(sample_file, "rb") as f:
        file_bytes = f.read()

    with app.app_context():
        result = process_csv_upload(
            application_type="BIPortal",
            upload_type="NORMAL",
            description="Insert servisi test yüklemesi",
            filename=sample_file.name,
            file_bytes=file_bytes,
            user_ip="127.0.0.1",
        )

    print("Test sonucu:")
    print(result)
