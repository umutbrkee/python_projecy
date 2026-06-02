"""
LDAP/Active Directory Servisi
Kullanıcı doğrulaması ve grup bilgileri
"""
import logging
from typing import Dict, Tuple, Optional, List
from ldap3 import Server, Connection, ALL, NTLM
from ldap3.core.exceptions import LDAPException

logger = logging.getLogger(__name__)


class LDAPService:
    """Active Directory LDAP entegrasyonu"""
    
    def __init__(
        self,
        ldap_server: str,
        ldap_port: int = 389,
        ldap_base_dn: str = "",
        use_ssl: bool = False,
        timeout: int = 10,
    ):
        """
        Args:
            ldap_server: LDAP sunucusu (örn: dc.ttnet.local)
            ldap_port: LDAP port (varsayılan: 389)
            ldap_base_dn: Base DN (örn: dc=ttnet,dc=local)
            use_ssl: SSL kullan (varsayılan: False)
            timeout: Bağlantı timeout saniye cinsinden
        """
        self.ldap_server = ldap_server
        self.ldap_port = ldap_port
        self.ldap_base_dn = ldap_base_dn
        self.use_ssl = use_ssl
        self.timeout = timeout
    
    def _normalize_group_name(self, group_dn: str) -> str:
        """
        LDAP DN'i normalize et
        cn=DWH_ADMINS_BO,ou=Groups,dc=ttnet,dc=local -> TTNET\\DWH_ADMINS_BO
        """
        try:
            # CN'i çıkar
            if "cn=" in group_dn.lower():
                parts = group_dn.split(",")
                cn_part = parts[0].split("=")[1].strip()
                return f"TTNET\\{cn_part}"
            return group_dn
        except Exception:
            return group_dn
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Kullanıcıyı LDAP ile doğrula ve grup bilgileri al
        
        Args:
            username: Kullanıcı adı (ör: jdoe, TTNet\\jdoe)
            password: Şifre
        
        Returns:
            (başarılı, kullanıcı_bilgisi_dict)
        """
        try:
            # Username'i normalize et
            if "\\" in username:
                # TTNET\jdoe formatını jdoe'ye çevir
                username = username.split("\\")[-1]
            
            # LDAP sunucusuna bağlan
            server = Server(
                self.ldap_server,
                port=self.ldap_port,
                use_ssl=self.use_ssl,
                get_info=ALL,
                connect_timeout=self.timeout,
            )
            
            # Kullanıcı DN'ini oluştur (basit interpolation)
            user_dn = f"cn={username},{self.ldap_base_dn}"
            
            # Bind et (username/password ile)
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                raise_exceptions=True,
            )
            
            if not conn.bind():
                logger.warning(f"LDAP bind başarısız: {username}")
                return False, None
            
            # Kullanıcı bilgileri ve grupları al
            conn.search(
                search_base=user_dn,
                search_filter="(objectclass=*)",
                attributes=["cn", "mail", "memberOf", "displayName"],
            )
            
            if not conn.entries:
                logger.warning(f"LDAP kullanıcı bulunamadı: {username}")
                conn.unbind()
                return False, None
            
            user_entry = conn.entries[0]
            
            # Grup bilgileri al (memberOf attribute'ından)
            groups = []
            if hasattr(user_entry, "memberOf"):
                for group_dn in user_entry.memberOf:
                    normalized_group = self._normalize_group_name(str(group_dn))
                    groups.append(normalized_group)
            
            conn.unbind()
            
            # Kullanıcı bilgisini döndür
            user_info = {
                "username": username,
                "display_name": str(user_entry.displayName[0]) if hasattr(user_entry, "displayName") else username,
                "email": str(user_entry.mail[0]) if hasattr(user_entry, "mail") else "",
                "groups": groups,
                "ldap_dn": user_dn,
            }
            
            logger.info(f"LDAP kimlik doğrulaması başarılı: {username}, Gruplar: {groups}")
            return True, user_info
        
        except LDAPException as e:
            logger.error(f"LDAP hatası ({username}): {str(e)}")
            return False, None
        except Exception as e:
            logger.error(f"Beklenmeyen hata ({username}): {str(e)}")
            return False, None


def create_ldap_service(
    ldap_server: str,
    ldap_port: int = 389,
    ldap_base_dn: str = "",
    use_ssl: bool = False,
    timeout: int = 10,
) -> LDAPService:
    """LDAP servis factory"""
    return LDAPService(
        ldap_server=ldap_server,
        ldap_port=ldap_port,
        ldap_base_dn=ldap_base_dn,
        use_ssl=use_ssl,
        timeout=timeout,
    )
