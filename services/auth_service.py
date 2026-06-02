"""
Auth Service - Kullanıcı doğrulama ve yetkilendirme
LDAP/Active Directory entegrasyonu
"""
import logging
from typing import Dict, Tuple, Optional
from services.ldap_service import create_ldap_service
from config import LDAP_ENABLED, LDAP_SERVER, LDAP_PORT, LDAP_BASE_DN, LDAP_USE_SSL, LDAP_TIMEOUT, LDAP_ALLOWED_GROUPS

logger = logging.getLogger(__name__)

# LDAP servis instance (lazy initialization)
_ldap_service = None


def get_ldap_service():
    """LDAP servis instance'ını al"""
    global _ldap_service
    if _ldap_service is None and LDAP_ENABLED:
        _ldap_service = create_ldap_service(
            ldap_server=LDAP_SERVER,
            ldap_port=LDAP_PORT,
            ldap_base_dn=LDAP_BASE_DN,
            use_ssl=LDAP_USE_SSL,
            timeout=LDAP_TIMEOUT,
        )
    return _ldap_service


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[Dict]]:
    """
    Kullanıcıyı LDAP/AD ile doğrula
    
    Args:
        username: Kullanıcı adı (ör: jdoe veya TTNET\\jdoe)
        password: Şifre
    
    Returns:
        (başarılı, kullanıcı_bilgisi)
    """
    if not LDAP_ENABLED:
        print("RAW LDAP_ENABLED:", LDAP_ENABLED)
        print("TYPE:", type(LDAP_ENABLED))
        logger.warning("LDAP etkinleştirilmemiş")
        return True, {
            "username": username,
            "groups": ["TTNET\\BO_Upload_Users"],
            "display_name": "Mock User"
        }
    
    ldap_service = get_ldap_service()
    if not ldap_service:
        logger.error("LDAP servis başlatılamadı")
        return False, None
    
    # LDAP ile doğrula
    success, user_info = ldap_service.authenticate(username, password)
    
    if not success or not user_info:
        return False, None
    
    # Kullanıcının izin verilen gruplardan birinde olup olmadığını kontrol et
    user_groups = user_info.get("groups", [])
    
    # İzin verilen grup kontrolü
    has_permission = any(
        allowed_group in user_groups 
        for allowed_group in LDAP_ALLOWED_GROUPS
    )
    
    if not has_permission:
        logger.warning(
            f"Kullanıcı yetkili grup'ta değil. Username: {username}, Gruplar: {user_groups}, "
            f"Gerekli: {LDAP_ALLOWED_GROUPS}"
        )
        return False, None
    
    # Session'a yazılacak user info oluştur
    session_user_info = {
        "username": user_info.get("username"),
        "display_name": user_info.get("display_name"),
        "email": user_info.get("email"),
        "groups": user_groups,
        "ldap_dn": user_info.get("ldap_dn"),
        "has_upload_permission": True,  # LDAP gruplarında varsa yükleme izni var
    }
    
    logger.info(f"Kimlik doğrulama başarılı: {username}, Gruplar: {user_groups}")
    return True, session_user_info


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
