# Hızlı Test Başlama (3 Dakika)

## 1. Mock Test (Rekomended - 30 Saniye)

```bash
python test_mock_ldap.py
```

**Beklenen Çıktı:**
```
test_authenticate_invalid_password ... ok
test_authenticate_unauthorized_group ... ok
test_authenticate_valid_user ... ok
test_check_user_groups ... ok
test_normalize_group_name ... ok
test_session_user_management ... ok

Ran 6 tests in 0.123s
OK
```

---

## 2. Flask App Test (1 Dakika)

```bash
python test_flask_app.py
```

**Beklenen Çıktı:**
```
============================================================
FLASK LOGIN INTEGRATION TEST'LERİ
============================================================
[TEST] Login sayfasına erişim... ✓
[TEST] Giriş olmadan ana sayfaya erişim redirection... ✓
[TEST] Ana sayfa...... ✓
[TEST] Geçmiş sayfasına erişim... ✓
[TEST] Logout işlemi... ✓
[TEST] Template'de user info... ✓

============================================================
✓ TÜM TEST'LER BAŞARILI!
============================================================
```

---

## 3. Gerçek LDAP Test (Opsiyonel - 2 Dakika)

### Adım 1: .env Hazırlama

```bash
# LDAP sunucusu ayarlarını değiştir
nano .env
```

```env
LDAP_ENABLED=True
LDAP_SERVER=dc.ttnet.local      # Kendi LDAP server'ını gir
LDAP_PORT=389
LDAP_BASE_DN=dc=ttnet,dc=local  # Kendi base DN'ni gir
LDAP_ALLOWED_GROUPS=TTNET\DWH_ADMINS_BO,TTNET\BO_Upload_Users
```

### Adım 2: İnteraktif Test

```bash
python test_ldap.py interactive
```

**Giriş:**
```
Kullanıcı adı (çıkmak için 'q'): jdoe
Şifre: ****
```

**Başarılı Çıktı:**
```
============================================================
Kullanıcı Doğrulama Testi: jdoe
============================================================
✓ Kimlik doğrulama başarılı!
  Username: jdoe
  Display Name: John Doe
  Email: jdoe@ttnet.local
  LDAP DN: cn=jdoe,dc=ttnet,dc=local
  Gruplar (2 adet):
    - TTNET\DWH_ADMINS_BO
    - TTNET\BO_Upload_Users

  İzin verilen gruplar kontrolü:
    Gerekli: ['TTNET\DWH_ADMINS_BO', 'TTNET\BO_Upload_Users']
    ✓ Kullanıcı yetkili grupta!
```

---

## 4. Browser Test (Opsiyonel - 2 Dakika)

### Mock LDAP ile (Hızlı)

```bash
# .env'i edit et
LDAP_ENABLED=False

# Uygulama başlat
python app.py
```

Tarayıcı açın:
```
http://localhost:5000/login
```

Dummy giriş:
- Username: `testuser`
- Password: `anypassword`

---

## Sorun Var mı?

### Test'ler Başarısız?

```bash
# Debug mode
python test_mock_ldap.py -v  # Daha detaylı çıktı
```

### LDAP Bağlantı Hatası?

```bash
# LDAP sunucusuna ping at
ping dc.ttnet.local

# .env kontrol et
cat .env | grep LDAP

# Test et
python test_ldap.py interactive
```

### Port Kilitli?

```bash
# Farklı port'ta başlat
python -c "from app import app; app.run(port=5001)"
```

---

## Next Steps

✅ Mock test'ler başarılı → **Hızlı güvenlik kontrolü tamamlandı**

✅ Flask test'leri başarılı → **Web app akışı çalışıyor**

✅ Gerçek LDAP test → **Production'a hazır**

---

## Komut Referansı

```bash
# 1. Unit test'leri
python test_mock_ldap.py

# 2. Integration test'ler
python test_flask_app.py

# 3. LDAP Interactive
python test_ldap.py interactive

# 4. LDAP Toplu
python test_ldap.py

# 5. Uygulama başlat
python app.py

# 6. Log ile debug
LDAP_DEBUG=1 python app.py
```

---

## Daha Detaylı Bilgi

Bkz: [TEST_GUIDE.md](TEST_GUIDE.md)

Sorunlar: [LDAP_SETUP.md](LDAP_SETUP.md) → Troubleshooting bölümü
