import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from werkzeug.utils import secure_filename
from services.db import db, init_db
from services.upload_service import process_csv_upload
from services.auth_service import authenticate_user, set_user_to_session, clear_user_from_session, get_user_from_session
from services.auth_decorators import login_required, authorize, upload_permission_required
from models import XUUpload
from config import ALLOWED_EXTENSIONS, APPLICATION_TYPES, UPLOAD_TYPES, SAMPLE_CSV_NAME, LDAP_ALLOWED_GROUPS
from datetime import timedelta
import logging
from dotenv import load_dotenv

load_dotenv()

# Logging ayarlaması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object("config")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-for-production")

# Session konfigürasyonu
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
app.config["SESSION_COOKIE_SECURE"] = False  # HTTPS için True yap
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

db.init_app(app)

# ESKİ decorator kaldırıldı
with app.app_context():
    init_db(app)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=8)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # Zaten giriş yapıldıysa ana sayfaya yönlendir
        if get_user_from_session(session):
            return redirect(url_for("index"))
        
        return render_template("login.html")
    
    # POST isteği - login denemesi
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    
    if not username or not password:
        return render_template(
            "login.html",
            error="Kullanıcı adı ve şifre gereklidir."
        )
    
    success, user_info = authenticate_user(username, password)
    
    if success and user_info:
        set_user_to_session(session, user_info)
        
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        
        flash(f"Hoş geldiniz, {user_info.get('display_name', username)}!", "success")
        return redirect(url_for("index"))
    
    return render_template(
        "login.html",
        error="Geçersiz kullanıcı adı veya şifre."
    )


@app.route("/logout")
def logout():
    user = get_user_from_session(session)
    if user:
        username = user.get("username", "Kullanıcı")
        logger.info(f"Çıkış: {username}")
    clear_user_from_session(session)
    flash("Çıkış yaptınız. Görüşmek üzere!", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    user = get_user_from_session(session)
    return render_template(
        "index.html",
        application_types=APPLICATION_TYPES,
        upload_types=UPLOAD_TYPES,
        sample_csv_name=SAMPLE_CSV_NAME,
        username=user.get("username") if user else "Kullanıcı",
    )

@app.route("/history")
@login_required
def history():
    user = get_user_from_session(session)
    uploads = XUUpload.query.order_by(XUUpload.uploadstartdate.desc()).limit(20).all()
    return render_template(
        "history.html", 
        uploads=uploads,
        username=user.get("username") if user else "Kullanıcı",
    )

@app.route("/download-sample")
@login_required
@authorize(LDAP_ALLOWED_GROUPS)
def download_sample():
    return send_from_directory("sample_data", SAMPLE_CSV_NAME, as_attachment=True)

@app.route("/submit", methods=["POST"])
@login_required
@authorize(LDAP_ALLOWED_GROUPS)
def submit():
    user = get_user_from_session(session)
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
    
    username = user.get("username", "unknown") if user else "unknown"

    result = process_csv_upload(
        application_type,
        upload_type,
        description,
        filename,
        file_bytes,
        request.remote_addr,
        username,
    )

    if result["success"]:
        logger.info(f"Dosya yükleme başarılı: {username}, Dosya: {filename}, Satırlar: {result['row_count']}")
        return render_template(
            "result.html",
            status="Başarılı",
            message=result["message"],
            row_count=result["row_count"],
            username=username,
        )

    logger.error(f"Dosya yükleme başarısız: {username}, Dosya: {filename}, Hata: {result['message']}")
    flash(result["message"], "danger")

    return render_template(
        "result.html",
        status="Başarısız",
        message=result["message"],
        row_count=result.get("row_count", 0),
        username=username,
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)