# Yeni Python CSV Yükleme Projesi

Bu proje, mevcut uygulamanın sadeleştirilmiş bir Python/Flask versiyonudur. Temel amaç:

- Kullanıcının bir `application type` ve `upload type` seçmesi
- Örnek CSV dosyasını indirme
- CSV dosyası yükleme
- `XU_UPLOAD` ve `XU_UPLOADDATA_V2` tablolarına kayıt ekleme
- SFTP, dosya taşıma ve kurumsal yetkilendirme mekanizmalarını şimdilik kaldırma

## Başlatma

1. Sanal ortam oluşturun ve etkinleştirin.
2. `pip install -r requirements.txt`
3. Aşağıdaki ortam değişkenlerinden biri mutlaka ayarlanmalıdır:
   - `DATABASE_URL` veya
   - `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`
   - ya da `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_HOST`, `ORACLE_PORT` ve `ORACLE_SERVICE_NAME`/`ORACLE_SID`
   - Örnek Oracle service name: `ORACLE_HOST=localhost`, `ORACLE_PORT=1521`, `ORACLE_SERVICE_NAME=XEDPB1`
   - Örnek Oracle SID: `ORACLE_HOST=localhost`, `ORACLE_PORT=1521`, `ORACLE_SID=XE`
4. `python app.py`
5. Tarayıcıyı açın: `http://127.0.0.1:5000`

> Not: Bu proje artık varsayılan olarak local SQLite yerine dıştaki veritabanına yazacak. Eğer bağlantı ayarlanmamışsa uygulama başlatılmaz.

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
