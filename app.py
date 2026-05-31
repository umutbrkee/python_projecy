from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from services.db import db, init_db
from services.upload_service import process_csv_upload
from models import XUUpload
from config import ALLOWED_EXTENSIONS, APPLICATION_TYPES, UPLOAD_TYPES, SAMPLE_CSV_NAME
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object("config")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-for-production")

db.init_app(app)

# ESKİ decorator kaldırıldı
with app.app_context():
    init_db(app)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template(
        "index.html",
        application_types=APPLICATION_TYPES,
        upload_types=UPLOAD_TYPES,
        sample_csv_name=SAMPLE_CSV_NAME,
    )

@app.route("/history")
def history():
    uploads = XUUpload.query.order_by(XUUpload.uploadstartdate.desc()).limit(20).all()
    return render_template("history.html", uploads=uploads)

@app.route("/download-sample")
def download_sample():
    return send_from_directory("sample_data", SAMPLE_CSV_NAME, as_attachment=True)

@app.route("/submit", methods=["POST"])
def submit():
    application_type = request.form.get("application_type")
    upload_type = request.form.get("upload_type")
    description = request.form.get("description", "").strip()
    csv_file = request.files.get("csv_file")

    if not application_type or not upload_type or not description:
        flash("Lütfen tüm alanları doldurun.", "warning")
        return redirect(url_for("index"))

    if csv_file is None or csv_file.filename == "":
        flash("CSV dosyası seçilmedi.", "warning")
        return redirect(url_for("index"))

    if not allowed_file(csv_file.filename):
        flash("Sadece CSV veya XLSX dosyaları yüklenebilir.", "danger")
        return redirect(url_for("index"))

    filename = secure_filename(csv_file.filename)
    file_bytes = csv_file.stream.read()

    result = process_csv_upload(
        application_type,
        upload_type,
        description,
        filename,
        file_bytes,
        request.remote_addr,
    )

    if result["success"]:
        return render_template(
            "result.html",
            status="Başarılı",
            message=result["message"],
            row_count=result["row_count"],
        )

    flash(result["message"], "danger")

    return render_template(
        "result.html",
        status="Başarısız",
        message=result["message"],
        row_count=result.get("row_count", 0),
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)