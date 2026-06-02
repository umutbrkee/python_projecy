# LDAP/Active Directory Entegrasyonu - Özet

## Yapılan Değişiklikler

### Yeni Dosyalar

1. **services/ldap_service.py**
   - `LDAPService` sınıfı — LDAP bind ve grup bilgisi
   - `create_ldap_service()` factory

2. **LDAP_SETUP.md**
   - Detaylı kurulum ve kullanım rehberi

3. **.env.example**
   - LDAP konfigürasyon şablonu

### Güncellenmiş Dosyalar

#### services/auth_service.py
- Eski statik ALLOWED_USERS dict'i kaldırıldı
- `authenticate_user()` LDAP entegrasyonu ile yeniden yazıldı
- LDAP_ALLOWED_GROUPS kontrolü eklendi
- Mevcut helper fonksiyonlar korundu:
  - `check_user_groups()`
  - `get_user_from_session()`
  - `set_user_to_session()`
  - `clear_user_from_session()`

#### services/auth_decorators.py
- Yeni `@authorize(required_groups)` decorator eklendi
- `@role_required()` korundu (backward compatibility)
- `@login_required` ve `@upload_permission_required` korundu

#### config.py
- LDAP ayarları eklendi:
  - `LDAP_ENABLED` (True/False)
  - `LDAP_SERVER`, `LDAP_PORT`
  - `LDAP_BASE_DN`
  - `LDAP_USE_SSL`, `LDAP_TIMEOUT`
  - `LDAP_ALLOWED_GROUPS`

#### app.py
- `authorize` import'u eklendi
- `/submit` ve `/download-sample` route'ları:
  - `@authorize(LDAP_ALLOWED_GROUPS)` kullanıyor
  - Eski `@upload_permission_required` kaldırıldı
- Logging eklendi (info/error)
- User display_name session'dan alınıyor

#### requirements.txt
- `ldap3>=3.4` eklendi

#### templates/login.html
- Test hesapları kaldırıldı
- AD entegrasyon mesajı eklendi

## Mevcut Koduyla Uyumluluk

✅ **Etkilenmedi:**
- `models.py` — XUUpload, XUUploadDataV2
- `services/db.py` — SQLAlchemy init
- `services/upload_service.py` — CSV işleme
- `services/oracle_connection.py` — Oracle bağlantı
- `templates/` diğer sayfalar

✅ **Backward Compat:**
- Mevcut decorator fonksiyonlar çalışır
- Session yapısı aynı
- Database sorgularında değişiklik yok

## Kullanım Örnekleri

### Temel Kurulum

```bash
pip install -r requirements.txt
cp .env.example .env
# .env'i düzenle
python app.py
```

### Route'u Koruma

```python
# Tüm izin verilen gruplara açık
@app.route("/upload")
@login_required
@authorize(LDAP_ALLOWED_GROUPS)
def upload():
    pass

# Spesifik gruplara açık
@app.route("/admin")
@login_required
@authorize(["TTNET\\DWH_ADMINS_BO"])
def admin():
    pass

# Sadece login gerekli (grup kontrolü yok)
@app.route("/dashboard")
@login_required
def dashboard():
    pass
```

### Session'dan User Bilgisi

```python
from services.auth_service import get_user_from_session
from flask import session

user = get_user_from_session(session)
print(user["username"])      # jdoe
print(user["display_name"])  # John Doe
print(user["groups"])        # ["TTNET\\DWH_ADMINS_BO", ...]
print(user["email"])         # jdoe@ttnet.local
```

## Önemli Konfigürasyonlar

### .env dosyası örneği

```env
LDAP_ENABLED=True
LDAP_SERVER=dc.ttnet.local
LDAP_PORT=389
LDAP_BASE_DN=dc=ttnet,dc=local
LDAP_USE_SSL=False
LDAP_TIMEOUT=10
LDAP_ALLOWED_GROUPS=TTNET\DWH_ADMINS_BO,TTNET\BO_Upload_Users
```

## Debug & Troubleshooting

### LDAP bağlantısı test etme

```python
from services.ldap_service import create_ldap_service

ldap = create_ldap_service(
    ldap_server="dc.ttnet.local",
    ldap_port=389,
    ldap_base_dn="dc=ttnet,dc=local"
)

success, user_info = ldap.authenticate("jdoe", "password")
print(success, user_info)
```

### Logs kontrol etme

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Şimdi tüm LDAP işlemleri debug seviyesinde loglanır
```

### DN formatı

Default: `cn=username,dc=ttnet,dc=local`

Eğer farklı ise, `ldap_service.py` satır 66'da düzenleyin:

```python
user_dn = f"cn={username},{self.ldap_base_dn}"  # Burayı değiştir
```

## Production Checklist

- [ ] `.env` güvenli şekilde ayarlandı
- [ ] `FLASK_SECRET_KEY` değiştirildi
- [ ] LDAP_SERVER production'a işaret ediyor
- [ ] LDAP_ALLOWED_GROUPS kontrol edildi
- [ ] SSL/HTTPS aktifleştirildi
- [ ] Logging seviyeleri ayarlandı
- [ ] LDAP timeout'ları optimize edildi
- [ ] User caching (opsiyonel) eklendi

## Destek

Sorular veya sorunlar için LDAP_SETUP.md dosyasını kontrol edin.
