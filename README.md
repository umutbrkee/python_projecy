# Yeni Python CSV Yükleme Projesi

Bu proje, mevcut uygulamanın sadeleştirilmiş bir Python/Flask versiyonudur. Temel amaç:

- Kullanıcının bir `application type` ve `upload type` seçmesi
- Örnek CSV dosyasını indirme
- CSV dosyası yükleme
- `XU_UPLOAD` ve `XU_UPLOADDATA_V2` tablolarına kayıt ekleme
- SFTP, dosya taşıma ve kurumsal yetkilendirme mekanizmalarını şimdilik kaldırma

## Kurulum ve Başlatma

### Yeni bir bilgisayarda kurulum (GitHub'dan klonlama)

1. Projeyi klonlayın:
   ```bash
   git clone <repository-url>
   cd python
   ```

2. Sanal ortam oluşturun ve etkinleştirin:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows (Set-ExecutionPolicy -Scope CurrentUser RemoteSigned) hata alırsa bunu çalıştır
   # ya da
   source .venv/bin/activate  # Linux/Mac
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. `.env` dosyası oluşturun:
   - `.env.example` dosyasını `.env` olarak kopyalayın
   - Kendi ortamınıza uygun değerleri düzenleyin
   ```bash
   copy .env.example .env  # Windows
   # ya da
   cp .env.example .env  # Linux/Mac
   ```

5. `.env` dosyasında aşağıdaki değerleri güncelle:
   - `ORACLE_USER` - Oracle kullanıcı adı
   - `ORACLE_PASSWORD` - Oracle şifresi
   - `ORACLE_HOST` - Oracle sunucusu (localhost veya IP)
   - `ORACLE_PORT` - Oracle portu (genelde 1521)
   - `ORACLE_SERVICE_NAME` - Service adı (XEPDB1 vb.)
   - `LDAP_ENABLED` - True/False (LDAP kullanıyorsa)
   - `FLASK_SECRET_KEY` - Güvenli bir anahtar ayarlayın

6. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

7. Tarayıcıyı açın: `http://127.0.0.1:5000`

> **Önemli:** `.env` dosyası asla GitHub'a commit edilmemelidir. `.gitignore` dosyasında zaten tanımlıdır. Her bilgisayarda kendi `.env` dosyasını oluşturmalısınız.

## Test: Oracle Insert Servisi

Yeni Oracle bağlantısı kurduğunuzda aşağıdaki betik ile insert servisini test edebilirsiniz:

```bash
python test_oracle_insert.py
```

Eğer `DATABASE_URL` kullanıyorsanız:

```bash
set DATABASE_URL=oracle+oracledb://system:1998@localhost:1521/XEDPB1
python test_oracle_insert.py
```

Doğrudan Oracle bağlanmasını doğrulamak için `services/oracle_connection.py` içindeki `validate_oracle_connection()` fonksiyonunu da kullanabilirsiniz.

## Proje Yapısı

- `app.py` - Flask uygulaması ve rota tanımları
- `config.py` - Konfigürasyon
- `services/db.py` - SQLAlchemy init
- `services/upload_service.py` - Dosya işleme servisleri
- `models.py` - Veri modeli tanımları
- `templates/` - HTML sayfalar
- `sample_data/AdslUplTempl.xlsx` - indirilebilir örnek CSV

## Gelecekteki genişletme

- Yetkilendirme ve sistem entegrasyonları sonraki aşamada tekrar eklenebilir.
- `XU_UPLOADDATA_V2` modeli ek bilgileri barındıracak şekilde genişletildi.
