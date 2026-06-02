# LDAP/Active Directory Entegrasyonu

## Genel Bakış

Bu uygulama, kullanıcı doğrulaması ve yetkilendirmesi için Active Directory (LDAP) entegrasyonunu destekler. C# ASP.NET MVC'deki `[Authorize(Roles = Constants.AllowedGroups)]` pattern'ı Python/Flask'e taşındı.

## Mimari

```
Login Form (login.html)
    ↓
app.py /login route
    ↓
auth_service.authenticate_user()
    ↓
ldap_service.authenticate() → LDAP bind
    ↓
memberOf attribute'ından grupları oku
    ↓
LDAP_ALLOWED_GROUPS ile kontrol et
    ↓
Session'a user info yaz
    ↓
@authorize decorator ile route koruması
```

## Kurulum

### 1. Gerekli Paketler

```bash
pip install -r requirements.txt
```

requirements.txt içinde:
- `ldap3>=3.4` — LDAP protokolü
- Diğer mevcut paketler

### 2. Ortam Değişkenleri

`.env.example`'i `.env` olarak kopyalayın ve şunları düzenleyin:

```env
# LDAP / Active Directory
LDAP_ENABLED=True
LDAP_SERVER=dc.ttnet.local          # LDAP sunucusu
LDAP_PORT=389                        # LDAP port (389=plain, 636=SSL)
LDAP_BASE_DN=dc=ttnet,dc=local       # Base DN
LDAP_USE_SSL=False                   # SSL etkinleştir
LDAP_TIMEOUT=10                      # Timeout (saniye)

# İzin verilen gruplar (virgülle ayrılmış)
LDAP_ALLOWED_GROUPS=TTNET\DWH_ADMINS_BO,TTNET\BO_Upload_Users

# Diğer ayarlar...
ORACLE_USER=system
ORACLE_PASSWORD=1998
FLASK_SECRET_KEY=your-secret-key
```

## Kullanım

### Login Akışı

1. Kullanıcı `/login` sayfasını açar
2. Username/password girer
3. `auth_service.authenticate_user()` çağrılır
4. `ldap_service.authenticate()` LDAP'a bağlanır:
   - `cn=jdoe,dc=ttnet,dc=local` formatında DN oluşturur
   - Username/password ile bind eder
   - memberOf attribute'ından AD grupları çıkartır
5. Gruplar `LDAP_ALLOWED_GROUPS` listesine göre kontrol edilir
6. Başarılıysa session'a user info yazılır

### Route Koruması

Örnek 1 — Tüm izin verilen gruplara açık:

```python
@app.route("/upload")
@login_required
@authorize(LDAP_ALLOWED_GROUPS)
def upload():
    user = get_user_from_session(session)
    return f"Hoş geldiniz, {user['username']}"
```

Örnek 2 — Spesifik grup kontrolü:

```python
@app.route("/admin")
@login_required
@authorize(["TTNET\\DWH_ADMINS_BO"])
def admin_panel():
    return "Sadece adminler erişebilir"
```

Örnek 3 — Sadece login gerekli:

```python
@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user_from_session(session)
    return render_template("dashboard.html", user=user)
```

## Kod Yapısı

### services/ldap_service.py

`LDAPService` sınıfı:
- `authenticate(username, password)` — LDAP doğrulaması
- `_normalize_group_name(group_dn)` — DN'i `TTNET\GroupName` formatına çevir

### services/auth_service.py

- `authenticate_user(username, password)` — LDAP ve grup kontrolü
- `check_user_groups(user_info, required_groups)` — Grup kontrol
- `get_user_from_session(session)` — Session'dan user al
- `set_user_to_session(session, user_info)` — Session'a user yaz
- `clear_user_from_session(session)` — Logout

### services/auth_decorators.py

- `@login_required` — Giriş gerekli
- `@authorize(required_groups)` — Belirli gruplara açık
- `@upload_permission_required` — Yükleme izni (mevcut uyumluluk)

## User Info Yapısı

Session'daki user bilgisi:

```python
{
    "username": "jdoe",
    "display_name": "John Doe",
    "email": "jdoe@ttnet.local",
    "groups": ["TTNET\\DWH_ADMINS_BO", "TTNET\\BO_Upload_Users"],
    "ldap_dn": "cn=jdoe,dc=ttnet,dc=local",
    "has_upload_permission": True
}
```

## Önemli Notlar

1. **LDAP DN Formatı**: Varsayılan olarak `cn=username,BASE_DN` formatı kullanılır. Eğer farklı bir format gerekliyse `ldap_service.py`'de `user_dn` satırını değiştirin.

2. **Group DN Normalization**: AD'deki `cn=DWH_ADMINS_BO,ou=Groups,dc=ttnet,dc=local` otomatik olarak `TTNET\DWH_ADMINS_BO`'ya çevrilir.

3. **Logging**: Tüm doğrulama ve hata işlemleri loglenir. `logger.info()` ve `logger.error()` kontrol edin.

4. **Production**: 
   - `FLASK_SECRET_KEY` güvenli bir şeye ayarlayın
   - `SESSION_COOKIE_SECURE=True` yapın (HTTPS gerekli)
   - Hata mesajlarını minimize edin (`app.py`'de logging seviyesini düzenleyin)

## Troubleshooting

### "LDAP bind başarısız"
- LDAP_SERVER ve LDAP_PORT kontrol edin
- Username formatını kontrol edin (TTNET\username vs username)
- Firewall kurallarını kontrol edin

### "Kullanıcı yetkili grup'ta değil"
- LDAP_ALLOWED_GROUPS'ta grup adlarını kontrol edin
- AD'deki tam grup DN'i çıkartmak için LDAP browser kullanın
- `_normalize_group_name()` fonksiyonunu debug edin

### LDAP zaman aşımı
- LDAP_TIMEOUT'u artırın
- Network bağlantısını kontrol edin
- LDAP_SERVER ip adresini deneyin

## Mevcut Kodla Uyumluluk

- SQLAlchemy ORM **etkilenmedi**
- Mevcut upload_service **etkilenmedi**
- Database modelleri **etkilenmedi**
- Sadece auth logic güncelleştirildi

## Gelecek Geliştirmeler

- [ ] LDAP connection pooling
- [ ] User caching (Redis)
- [ ] Audit logging (LDAP bind attempts)
- [ ] Multi-domain AD support
- [ ] OAuth2 / OpenID Connect (isteğe bağlı)
