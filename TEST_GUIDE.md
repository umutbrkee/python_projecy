# LDAP Login Sistemi Test Rehberi

## Test Seçenekleri

### 1. Mock Test (Hızlı, Gerçek LDAP gerekmez)

```bash
# Unit test'ler
python -m pytest test_mock_ldap.py -v

# veya
python test_mock_ldap.py
```

**Avantajlar:**
- ✓ Gerçek LDAP server gerekmez
- ✓ Hızlı çalışır
- ✓ CI/CD pipeline'larda kullanılabilir
- ✓ Mock kullanıcılar önceden tanımlı

**Dezavantajlar:**
- ✗ Gerçek LDAP'ı test etmez

### 2. Flask App Integration Test

```bash
python test_flask_app.py
```

**Test eder:**
- Login page erişimi
- Giriş olmadan redirection
- Session yönetimi
- Logout
- Template'de user info gösterimi

**Avantajlar:**
- ✓ Tüm Flask flow'u test eder
- ✓ Mock LDAP kullanır (hızlı)
- ✓ UI/template test'leri var

### 3. Gerçek LDAP Test

#### 3.1 İnteraktif Mode

```bash
python test_ldap.py interactive
```

Çalışır ve şunları sorar:
```
======================================
LDAP Sunucusu Bağlantı Testi
======================================
LDAP_SERVER: dc.ttnet.local
LDAP_PORT: 389
LDAP_BASE_DN: dc=ttnet,dc=local
...

Kullanıcı adı (çıkmak için 'q'): jdoe
Şifre: ****

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

#### 3.2 Toplu Test Mode

Önce `test_ldap.py`'i düzenle:

```python
if __name__ == "__main__":
    test_users = [
        ("jdoe", "password123"),
        ("user1", "pass456"),
        ("admin", "admin789"),
    ]
    batch_test(test_users)
```

Sonra çalıştır:
```bash
python test_ldap.py
```

### 4. Browser ile Test

#### 4.1 İlk Başlangıç

```bash
python app.py
```

Tarayıcı açın:
```
http://localhost:5000/login
```

#### 4.2 LDAP Etkinleştirilmiş Durumda

1. `.env` dosyasını ayarla:

```env
LDAP_ENABLED=True
LDAP_SERVER=dc.ttnet.local
LDAP_PORT=389
LDAP_BASE_DN=dc=ttnet,dc=local
LDAP_USE_SSL=False
LDAP_TIMEOUT=10
LDAP_ALLOWED_GROUPS=TTNET\DWH_ADMINS_BO,TTNET\BO_Upload_Users
```

2. Uygulama başlat:

```bash
python app.py
```

3. Login dene:
   - Username: `jdoe` (AD kullanıcısı)
   - Password: AD şifresi

#### 4.3 Debug Mode'da

Tüm LDAP işlemlerini log olarak görmek için:

```python
# app.py başında ekle veya .env'de ayarla
import logging
logging.basicConfig(level=logging.DEBUG)
```

Sonra çalıştır:
```bash
python app.py
```

Tarayıcıda her işlem terminalde loglanacak.

---

## Kurulum Adımları

### Adım 1: Gerekli Paketler

```bash
pip install -r requirements.txt
pip install pytest pytest-mock  # Test paketleri (opsiyonel)
```

### Adım 2: .env Dosyası

```bash
cp .env.example .env
# .env'i edit et
```

### Adım 3: Test Seçimi

#### Seçenek A: Mock Test (Önerilen başlangıç)

```bash
# Hızlı unit test'ler
python test_mock_ldap.py

# Flask integration test'leri
python test_flask_app.py
```

#### Seçenek B: Gerçek LDAP Test

```bash
# İnteraktif mode
python test_ldap.py interactive

# Toplu test (test_ldap.py'i düzenle)
python test_ldap.py
```

#### Seçenek C: Tarayıcı Test

```bash
python app.py
# Tarayıcı: http://localhost:5000/login
```

---

## Test Senaryoları

### Senaryo 1: Başarılı Login

**Giriş:**
- Username: `jdoe`
- Password: `actual_ad_password`

**Beklenen:**
- ✓ Login başarılı
- ✓ Index page'e redirect
- ✓ Kullanıcı adı header'da gösterilir
- ✓ Session oluşturulur

### Senaryo 2: Yanlış Şifre

**Giriş:**
- Username: `jdoe`
- Password: `wrongpassword`

**Beklenen:**
- ✗ "Geçersiz kullanıcı adı veya şifre" hatası
- ✓ Login sayfasında kalır

### Senaryo 3: Yetkisiz Grup

**Giriş:**
- Username: `otheruser` (TTNET\OtherGroup'ta)
- Password: `correct_password`

**Beklenen:**
- ✗ "Geçersiz kullanıcı adı veya şifre" hatası
- ✓ Login sayfasında kalır (grup kontrolü başarısız)

### Senaryo 4: Logout

**İşlem:**
1. Login yap
2. Logout link'ine tıkla

**Beklenen:**
- ✓ Session temizleniyor
- ✓ Login sayfasına yönlendiriliyor

### Senaryo 5: Korunan Sayfaya Erişim

**Giriş olmadan:**
```
GET /history
→ 302 Redirect to /login
```

**Login sonrası:**
```
GET /history
→ 200 OK (Geçmiş listesi gösterilir)
```

---

## Hata Ayıklama

### Sorun: "LDAP bind başarısız"

**Kontrol Listesi:**

1. LDAP_SERVER'a ping at
```bash
ping dc.ttnet.local
```

2. Port açık mı kontrol et
```bash
# Windows
netstat -an | findstr 389
# Linux
netsh interface tcp show tcpstats | findstr 1521
```

3. .env ayarlarını kontrol et
```bash
cat .env | grep LDAP
```

4. Username formatını kontrol et (DN'yi bulma)
```bash
# LDAP Browser veya ldapsearch kullan
# docker run -it nicolaka/netshoot ldapsearch -x -h dc.ttnet.local -D "cn=admin,dc=ttnet,dc=local" -W
```

### Sorun: "Kullanıcı grup'ta değil"

**Kontrol Listesi:**

1. LDAP_ALLOWED_GROUPS formatı kontrol et
```env
# Yanlış:
LDAP_ALLOWED_GROUPS=DWH_ADMINS_BO

# Doğru:
LDAP_ALLOWED_GROUPS=TTNET\DWH_ADMINS_BO
```

2. Kullanıcının gerçek gruplarını kontrol et
```bash
# ldapsearch kullan
ldapsearch -x -h dc.ttnet.local -b "dc=ttnet,dc=local" "uid=jdoe" memberOf
```

3. Log output'unu kontrol et
```python
# test_ldap.py çalıştırıp groups'ı görüntüle
python test_ldap.py interactive
# Username: jdoe
# Password: ****
# Çıktıda "Gruplar" bölümünü kontrol et
```

### Sorun: "LDAP zaman aşımı"

**Çözüm:**

1. LDAP_TIMEOUT'u artır
```env
LDAP_TIMEOUT=30
```

2. LDAP_SERVER'ı IP adresle dene
```env
LDAP_SERVER=192.168.1.100
```

---

## Log Output Örnekleri

### Başarılı Login
```
[INFO] LDAP kimlik doğrulaması başarılı: jdoe, Gruplar: ['TTNET\\DWH_ADMINS_BO', 'TTNET\\BO_Upload_Users']
[INFO] Kimlik doğrulama başarılı: jdoe, Gruplar: [...]
[INFO] Dosya yükleme başarılı: jdoe, Dosya: test.xlsx, Satırlar: 100
```

### Başarısız Login
```
[WARNING] LDAP bind başarısız: jdoe
[WARNING] Kullanıcı yetkili grup'ta değil. Username: user1, Gruplar: ['TTNET\\OtherGroup'], Gerekli: [...]
[ERROR] LDAP hatası (jdoe): Connection refused
```

---

## Pytest ile Test Çalıştırma (Opsiyonel)

Test framework'ü tercih ediyorsan:

```bash
# Tüm test'leri çalıştır
pytest test_mock_ldap.py -v

# Belirli test'i çalıştır
pytest test_mock_ldap.py::TestAuthService::test_authenticate_valid_user -v

# Coverage raporu
pytest test_mock_ldap.py --cov=services.auth_service
```

---

## Özet

| Test Türü | Komut | Hız | LDAP Gerekli |
|-----------|-------|------|--------------|
| Unit (Mock) | `python test_mock_ldap.py` | ⚡ Çok Hızlı | ❌ Hayır |
| Integration | `python test_flask_app.py` | ⚡ Hızlı | ❌ Hayır |
| LDAP Interactive | `python test_ldap.py interactive` | 🐢 Yavaş | ✅ Evet |
| LDAP Batch | `python test_ldap.py` | 🐢 Yavaş | ✅ Evet |
| Browser | `python app.py` + Tarayıcı | 🐢 Yavaş | ✅ Evet |

**Önerilen Test Akışı:**

1. **İlk geliştirme:** Unit test'ler (`test_mock_ldap.py`)
2. **Feature tamamlandı:** Integration test'leri (`test_flask_app.py`)
3. **Production hazırlığı:** Gerçek LDAP test'leri (`test_ldap.py interactive`)
4. **Deploy:** Tarayıcı test'i
