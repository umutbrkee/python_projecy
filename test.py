from ldap3 import Server, Connection
from config import LDAP_SERVER, LDAP_PORT

server = Server(LDAP_SERVER, port=LDAP_PORT)

conn = Connection(server)

print("LDAP connect deniyor...")

if conn.bind():
    print("LDAP BAĞLANTI OK")
else:
    print("LDAP BAĞLANTI FAIL")