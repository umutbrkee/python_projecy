"""
Flask App Integration Test
Tüm login flow'unu test et
"""
import os
import sys
from flask import session as flask_session
from unittest.mock import patch, MagicMock

# .env'i test modu için yükle
os.environ['LDAP_ENABLED'] = 'False'  # Mock kullanacağız

from app import app
from services.auth_service import set_user_to_session


class FlaskLoginTestSuite:
    """Flask login flow test'leri"""
    
    def __init__(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_login_page(self):
        """Test: Login sayfası erişim"""
        print("\n[TEST] Login sayfasına erişim...", end=" ")
        response = self.client.get('/login')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert b'Kullan' in response.data or b'login' in response.data.lower(), "Login formu bulunamadı"
        print("✓")
    
    def test_redirect_to_login_when_not_authenticated(self):
        """Test: Login olmadan ana sayfaya giremez"""
        print("[TEST] Giriş olmadan ana sayfaya erişim redirection...", end=" ")
        response = self.client.get('/', follow_redirects=False)
        assert response.status_code in [301, 302, 307, 308], f"Expected redirect, got {response.status_code}"
        assert 'login' in response.location.lower(), "Login'e redirect olmadı"
        print("✓")
    
    def test_redirect_to_index_when_authenticated(self):
        """Test: Login olmuşsa index'e yönlendir"""
        print("[TEST] Giriş yapmışken index'e yönlendirme...", end=" ")
        with self.client:
            with self.client.session_transaction() as sess:
                set_user_to_session(sess, {
                    "username": "testuser",
                    "display_name": "Test User",
                    "groups": ["TTNET\\BO_Upload_Users"],
                    "has_upload_permission": True
                })
            
            response = self.client.get('/login', follow_redirects=False)
            assert response.status_code in [301, 302, 307, 308], f"Expected redirect, got {response.status_code}"
            print("✓")
    
    def test_index_page_with_auth(self):
        """Test: Login sonrası ana sayfa erişim"""
        print("[TEST] Giriş sonrası ana sayfa...", end=" ")
        with self.client:
            with self.client.session_transaction() as sess:
                set_user_to_session(sess, {
                    "username": "testuser",
                    "display_name": "Test User",
                    "groups": ["TTNET\\BO_Upload_Users"],
                    "has_upload_permission": True
                })
            
            response = self.client.get('/')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            assert b'CSV' in response.data or b'Y' in response.data[:500], "Ana sayfa içeriği bulunamadı"
            print("✓")
    
    def test_history_page_with_auth(self):
        """Test: Geçmiş sayfasına erişim"""
        print("[TEST] Geçmiş sayfasına erişim...", end=" ")
        with self.client:
            with self.client.session_transaction() as sess:
                set_user_to_session(sess, {
                    "username": "testuser",
                    "display_name": "Test User",
                    "groups": ["TTNET\\BO_Upload_Users"],
                    "has_upload_permission": True
                })
            
            response = self.client.get('/history')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            print("✓")
    
    def test_logout(self):
        """Test: Logout işlemi"""
        print("[TEST] Logout işlemi...", end=" ")
        with self.client:
            # Önce login
            with self.client.session_transaction() as sess:
                set_user_to_session(sess, {
                    "username": "testuser",
                    "display_name": "Test User",
                    "groups": ["TTNET\\BO_Upload_Users"],
                    "has_upload_permission": True
                })
            
            # Logout yap
            response = self.client.get('/logout', follow_redirects=False)
            assert response.status_code in [301, 302, 307, 308], f"Expected redirect, got {response.status_code}"
            
            # Session'dan sil mi kontrol et
            with self.client.session_transaction() as sess:
                assert 'user' not in sess or sess.get('user') is None, "User session'dan silinmedi"
            print("✓")
    
    def test_user_info_in_template(self):
        """Test: Şablon'da user info gösterme"""
        print("[TEST] Template'de user info...", end=" ")
        with self.client:
            with self.client.session_transaction() as sess:
                set_user_to_session(sess, {
                    "username": "johndoe",
                    "display_name": "John Doe",
                    "groups": ["TTNET\\BO_Upload_Users"],
                    "has_upload_permission": True
                })
            
            response = self.client.get('/')
            assert b'John Doe' in response.data or b'johndoe' in response.data, "User info template'de gösterilmiyor"
            print("✓")
    
    def run_all_tests(self):
        """Tüm test'leri çalıştır"""
        print("\n" + "="*60)
        print("FLASK LOGIN INTEGRATION TEST'LERİ")
        print("="*60)
        
        try:
            self.test_login_page()
            self.test_redirect_to_login_when_not_authenticated()
            self.test_index_page_with_auth()
            self.test_redirect_to_index_when_authenticated()
            self.test_history_page_with_auth()
            self.test_logout()
            self.test_user_info_in_template()
            
            print("\n" + "="*60)
            print("✓ TÜM TEST'LER BAŞARILI!")
            print("="*60)
            return True
        except AssertionError as e:
            print(f"\n✗ TEST BAŞARIŞIZ: {e}")
            print("="*60)
            return False
        except Exception as e:
            print(f"\n✗ BEKLENMEYEN HATA: {e}")
            import traceback
            traceback.print_exc()
            print("="*60)
            return False


if __name__ == '__main__':
    test_suite = FlaskLoginTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)
