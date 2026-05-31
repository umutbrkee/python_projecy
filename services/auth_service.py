"""
Auth Service - Kullanıcı doğrulama ve yetkilendirme
AllowedGroups kontrolü ve login yönetimi
"""
import hashlib
from typing import Dict, Tuple, Optional

# Önceden tanımlı kullanıcılar ve izin verilen gruplar
# Gerçek ortamda bu bir veritabanında olacak ve şifreler hash'lenmiş olacak
ALLOWED_USERS = {
    "admin": {
        "password": "admin123",  # Üretim ortamında hash'lenmiş olmalı
        "groups": ["admin", "upload_users"]
    },
    "biportals": {
        "password": "biportal2024",
        "groups": ["upload_users"]
    },
    "user1": {
        "password": "user123",
        "groups": ["upload_users"]
    }
}

ALLOWED_GROUPS = ["admin", "upload_users"]


def hash_password(password: str) -> str:
    """Şifre hash'leme"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Şifre doğrulama
    Gerçek ortamda bcrypt gibi bir kütüphane kullanılmalı
    """
    # Basit komparizyon için şimdilik düz metin kullanıyoruz
    # Üretim için: bcrypt.checkpw() kullan
    return plain_password == stored_password


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[Dict]]:
    """
    Kullanıcıyı doğrula
    
    Returns:
        (başarılı, kullanıcı_bilgisi)
    """
    user = ALLOWED_USERS.get(username)
    
    if not user:
        return False, None
    
    if not verify_password(password, user["password"]):
        return False, None
    
    # Kullanıcının en az bir izin verilen grup'ta olması gerekli
    user_groups = user.get("groups", [])
    if not any(g in ALLOWED_GROUPS for g in user_groups):
        return False, None
    
    return True, {
        "username": username,
        "groups": user_groups,
        "has_upload_permission": "upload_users" in user_groups
    }


def check_user_groups(user_info: Dict, required_groups: list) -> bool:
    """
    Kullanıcının gerekli gruplardan birine ait olup olmadığını kontrol et
    
    Args:
        user_info: authenticate_user tarafından dönen kullanıcı bilgisi
        required_groups: gerekli gruplar listesi
    
    Returns:
        En az bir grup'ta varsa True
    """
    if not user_info:
        return False
    
    user_groups = user_info.get("groups", [])
    return any(g in user_groups for g in required_groups)


def validate_upload_permission(user_info: Dict) -> bool:
    """
    Kullanıcının yükleme izni olup olmadığını kontrol et
    """
    if not user_info:
        return False
    
    return user_info.get("has_upload_permission", False)


def get_user_from_session(session: dict) -> Optional[Dict]:
    """
    Session'dan kullanıcı bilgisini al
    """
    return session.get("user")


def set_user_to_session(session: dict, user_info: Dict) -> None:
    """
    Session'a kullanıcı bilgisini kaydet
    """
    session["user"] = user_info
    session.permanent = True


def clear_user_from_session(session: dict) -> None:
    """
    Session'dan kullanıcı bilgisini sil
    """
    if "user" in session:
        del session["user"]
