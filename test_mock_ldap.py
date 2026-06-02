"""
Mock LDAP Test
Gerçek LDAP server olmadan test etmek için
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from services.auth_service import authenticate_user, check_user_groups, get_user_from_session, set_user_to_session
from services.auth_decorators import login_required, authorize
from flask import Flask, session


class MockLDAPService:
    """Mock LDAP Servisi"""
    
    def __init__(self):
        self.users = {
            "jdoe": {
                "password": "password123",
                "display_name": "John Doe",
                "email": "jdoe@ttnet.local",
                "groups": ["TTNET\\DWH_ADMINS_BO", "TTNET\\BO_Upload_Users"]
            },
            "user1": {
                "password": "pass123",
                "display_name": "User One",
                "email": "user1@ttnet.local",
                "groups": ["TTNET\\BO_Upload_Users"]
            },
            "unauthorized": {
                "password": "pass123",
                "display_name": "Unauthorized User",
                "email": "unauthorized@ttnet.local",
                "groups": ["TTNET\\OtherGroup"]
            }
        }
    
    def authenticate(self, username, password):
        """Mock authenticate method"""
        user = self.users.get(username)
        
        if not user:
            return False, None
        
        if user["password"] != password:
            return False, None
        
        return True, {
            "username": username,
            "display_name": user["display_name"],
            "email": user["email"],
            "groups": user["groups"],
            "ldap_dn": f"cn={username},dc=ttnet,dc=local"
        }


class TestAuthService(unittest.TestCase):
    """Auth Service test'leri"""
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret'
        self.client = self.app.test_client()
    
    @patch('services.auth_service.get_ldap_service')
    @patch('services.auth_service.LDAP_ENABLED', True)
    @patch('services.auth_service.LDAP_ALLOWED_GROUPS', 
           ["TTNET\\DWH_ADMINS_BO", "TTNET\\BO_Upload_Users"])
    def test_authenticate_valid_user(self, mock_get_ldap):
        """Test: Yetkili kullanıcı doğrulaması"""
        mock_ldap = MockLDAPService()
        mock_get_ldap.return_value = mock_ldap
        
        success, user_info = authenticate_user("jdoe", "password123")
        
        self.assertTrue(success)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info["username"], "jdoe")
        self.assertEqual(user_info["display_name"], "John Doe")
        self.assertTrue(user_info["has_upload_permission"])
    
    @patch('services.auth_service.get_ldap_service')
    @patch('services.auth_service.LDAP_ENABLED', True)
    @patch('services.auth_service.LDAP_ALLOWED_GROUPS',
           ["TTNET\\DWH_ADMINS_BO", "TTNET\\BO_Upload_Users"])
    def test_authenticate_invalid_password(self, mock_get_ldap):
        """Test: Yanlış şifre"""
        mock_ldap = MockLDAPService()
        mock_get_ldap.return_value = mock_ldap
        
        success, user_info = authenticate_user("jdoe", "wrongpassword")
        
        self.assertFalse(success)
        self.assertIsNone(user_info)
    
    @patch('services.auth_service.get_ldap_service')
    @patch('services.auth_service.LDAP_ENABLED', True)
    @patch('services.auth_service.LDAP_ALLOWED_GROUPS',
           ["TTNET\\DWH_ADMINS_BO", "TTNET\\BO_Upload_Users"])
    def test_authenticate_unauthorized_group(self, mock_get_ldap):
        """Test: Yetkisiz grup"""
        mock_ldap = MockLDAPService()
        mock_get_ldap.return_value = mock_ldap
        
        success, user_info = authenticate_user("unauthorized", "pass123")
        
        self.assertFalse(success)
        self.assertIsNone(user_info)
    
    def test_check_user_groups(self):
        """Test: Grup kontrolü"""
        user_info = {
            "username": "jdoe",
            "groups": ["TTNET\\DWH_ADMINS_BO", "TTNET\\BO_Upload_Users"]
        }
        
        # Test: Var olan grup
        result = check_user_groups(user_info, ["TTNET\\DWH_ADMINS_BO"])
        self.assertTrue(result)
        
        # Test: Olmayan grup
        result = check_user_groups(user_info, ["TTNET\\OtherGroup"])
        self.assertFalse(result)
        
        # Test: Multiple gruplardan biri var
        result = check_user_groups(
            user_info, 
            ["TTNET\\OtherGroup", "TTNET\\BO_Upload_Users"]
        )
        self.assertTrue(result)
    
    def test_session_user_management(self):
        """Test: Session user yönetimi"""
        with self.app.test_request_context():
            user_info = {
                "username": "jdoe",
                "display_name": "John Doe",
                "groups": ["TTNET\\DWH_ADMINS_BO"]
            }
            
            # Session'a yaz
            set_user_to_session(session, user_info)
            
            # Session'dan oku
            retrieved = get_user_from_session(session)
            
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved["username"], "jdoe")
            self.assertEqual(retrieved["display_name"], "John Doe")


class TestAuthDecorators(unittest.TestCase):
    """Auth Decorators test'leri"""
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret'
        self.client = self.app.test_client()
    
    def test_login_required_redirect(self):
        """Test: @login_required - redirect to login"""
        from services.auth_decorators import login_required
        from flask import redirect, url_for
        
        @self.app.route('/protected')
        @login_required
        def protected_route():
            return 'Protected Content'
        
        @self.app.route('/login')
        def login():
            return 'Login Page'
        
        # Login olmadan test
        with self.client:
            response = self.client.get('/protected')
            # Redirect bekliyoruz
            self.assertIn(response.status_code, [301, 302, 307, 308])
    
    def test_authorize_with_user(self):
        """Test: @authorize with authorized user"""
        from services.auth_decorators import authorize
        
        @self.app.route('/admin')
        @authorize(["TTNET\\DWH_ADMINS_BO"])
        def admin_route():
            return 'Admin Page'
        
        @self.app.route('/login')
        def login():
            return 'Login Page'
        
        with self.app.test_request_context():
            set_user_to_session(session, {
                "username": "jdoe",
                "groups": ["TTNET\\DWH_ADMINS_BO"]
            })
            
            with self.client:
                response = self.client.get('/admin')
                # 200 veya redirect bekliyoruz (test context'e bağlı)


class TestLDAPServiceNormalization(unittest.TestCase):
    """LDAP Service normalization test'leri"""
    
    @patch('services.ldap_service.logger')
    def test_normalize_group_name(self, mock_logger):
        """Test: Group DN normalization"""
        from services.ldap_service import create_ldap_service
        
        ldap_service = create_ldap_service(
            ldap_server="dc.ttnet.local",
            ldap_base_dn="dc=ttnet,dc=local"
        )
        
        # Test case 1: Normal AD DN
        result = ldap_service._normalize_group_name(
            "cn=DWH_ADMINS_BO,ou=Groups,dc=ttnet,dc=local"
        )
        self.assertEqual(result, "TTNET\\DWH_ADMINS_BO")
        
        # Test case 2: Different group
        result = ldap_service._normalize_group_name(
            "cn=BO_Upload_Users,ou=Groups,dc=ttnet,dc=local"
        )
        self.assertEqual(result, "TTNET\\BO_Upload_Users")


if __name__ == '__main__':
    unittest.main(verbosity=2)
