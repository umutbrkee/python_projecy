"""
Login dekoratörü ve middleware'ler
LDAP/AD grup yetkilendirmesi desteği
"""
from functools import wraps
from flask import redirect, url_for, session, request
from services.auth_service import get_user_from_session, check_user_groups


def login_required(f):
    """
    Flask rotusu için login gerekli decorator
    (C#'deki [Authorize] gibi)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_session(session)
        if not user:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def authorize(required_groups: list = None):
    """
    Belirli LDAP/AD gruplarına sahip kullanıcılar için decorator
    (C#'deki [Authorize(Roles = Constants.AllowedGroups)] gibi)
    
    Kullanım:
        @app.route("/upload")
        @authorize(["TTNET\\BO_Upload_Users", "TTNET\\DWH_ADMINS_BO"])
        def upload():
            ...
    
    Args:
        required_groups: Gerekli AD grup listesi
    """
    if required_groups is None:
        required_groups = []
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_user_from_session(session)
            
            if not user:
                return redirect(url_for("login", next=request.url))
            
            # Eğer grup kontrolü yapılacaksa
            if required_groups:
                if not check_user_groups(user, required_groups):
                    return "Erişim Reddedildi - Yetkisiz Grup", 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(required_groups):
    """
    Belirli gruplara sahip kullanıcılar için decorator (eski isim uyumluluğu)
    
    Kullanım:
        @app.route("/admin")
        @role_required(["admin"])
        def admin_panel():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_user_from_session(session)
            
            if not user:
                return redirect(url_for("login", next=request.url))
            
            if not check_user_groups(user, required_groups):
                return "Erişim Reddedildi", 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def upload_permission_required(f):
    """
    Sadece yükleme izni olan kullanıcılar için decorator
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_session(session)
        
        if not user:
            return redirect(url_for("login", next=request.url))
        
        if not user.get("has_upload_permission"):
            return "Yükleme izniniz yok", 403
        
        return f(*args, **kwargs)
    return decorated_function
