"""
LDAP Servisi Test Script
Gerçek LDAP bağlantısını test etmek için kullanın
"""
import os
import sys
import logging
from services.ldap_service import create_ldap_service
from config import LDAP_SERVER, LDAP_PORT, LDAP_BASE_DN, LDAP_USE_SSL, LDAP_TIMEOUT, LDAP_ALLOWED_GROUPS

# Logging ayarla
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ldap_connection():
    """LDAP sunucusuna bağlanabilir mi test et"""
    print("\n" + "="*60)
    print("LDAP Sunucusu Bağlantı Testi")
    print("="*60)
    print(f"LDAP_SERVER: {LDAP_SERVER}")
    print(f"LDAP_PORT: {LDAP_PORT}")
    print(f"LDAP_BASE_DN: {LDAP_BASE_DN}")
    print(f"LDAP_USE_SSL: {LDAP_USE_SSL}")
    print(f"LDAP_TIMEOUT: {LDAP_TIMEOUT}")
    print("="*60)
    
    try:
        ldap_service = create_ldap_service(
            ldap_server=LDAP_SERVER,
            ldap_port=LDAP_PORT,
            ldap_base_dn=LDAP_BASE_DN,
            use_ssl=LDAP_USE_SSL,
            timeout=LDAP_TIMEOUT,
        )
        print("✓ LDAP servis oluşturuldu")
        return ldap_service
    except Exception as e:
        print(f"✗ LDAP servis oluşturulurken hata: {e}")
        return None


def test_user_authentication(ldap_service, username, password):
    """Kullanıcı doğrulamasını test et"""
    print(f"\n{'='*60}")
    print(f"Kullanıcı Doğrulama Testi: {username}")
    print("="*60)
    
    success, user_info = ldap_service.authenticate(username, password)
    
    if success and user_info:
        print("✓ Kimlik doğrulama başarılı!")
        print(f"  Username: {user_info['username']}")
        print(f"  Display Name: {user_info['display_name']}")
        print(f"  Email: {user_info['email']}")
        print(f"  LDAP DN: {user_info['ldap_dn']}")
        print(f"  Gruplar ({len(user_info['groups'])} adet):")
        for group in user_info['groups']:
            print(f"    - {group}")
        
        # Izin verilen gruplar kontrolü
        print(f"\n  İzin verilen gruplar kontrolü:")
        print(f"    Gerekli: {LDAP_ALLOWED_GROUPS}")
        
        has_permission = any(
            allowed_group in user_info['groups']
            for allowed_group in LDAP_ALLOWED_GROUPS
        )
        
        if has_permission:
            print(f"    ✓ Kullanıcı yetkili grupta!")
        else:
            print(f"    ✗ Kullanıcı yetkili grupta DEĞIL!")
        
        return True, user_info
    else:
        print("✗ Kimlik doğrulama başarısız!")
        return False, None


def interactive_test():
    """İnteraktif test modu"""
    ldap_service = test_ldap_connection()
    if not ldap_service:
        return
    
    while True:
        print("\n" + "-"*60)
        username = input("Kullanıcı adı (çıkmak için 'q'): ").strip()
        if username.lower() == 'q':
            break
        
        password = input("Şifre: ")
        
        test_user_authentication(ldap_service, username, password)


def batch_test(test_users):
    """Toplu test modu
    
    Args:
        test_users: [(username, password), ...]
    """
    ldap_service = test_ldap_connection()
    if not ldap_service:
        return
    
    results = []
    for username, password in test_users:
        success, user_info = test_user_authentication(ldap_service, username, password)
        results.append({
            "username": username,
            "success": success,
            "user_info": user_info
        })
    
    # Özet
    print("\n" + "="*60)
    print("Test Sonuçları Özeti")
    print("="*60)
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"{status} {result['username']}")
    
    print(f"\nToplam: {len(results)}, Başarılı: {sum(1 for r in results if r['success'])}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        # İnteraktif mod: python test_ldap.py interactive
        interactive_test()
    else:
        # Batch mod: python test_ldap.py
        print("Toplu test modu - belirli kullanıcıları test etmek için aşağıdaki satırları değiştirin:")
        print("test_users = [")
        print('    ("jdoe", "password123"),')
        print('    ("user1", "pass123"),')
        print("]")
        print("\nveya\n")
        print("İnteraktif mod kullanın:")
        print("python test_ldap.py interactive")
