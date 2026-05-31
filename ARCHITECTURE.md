# Mimari ve Taşınan Bileşenler

## Amaç
Bu proje, mevcut uygulamanın ekran ve iş akışını koruyarak Python/Flask tabanlı yeni bir uygulama olarak yeniden geliştirildi. Mevcut projedeki SFTP, dosya aktarımı ve yetkilendirme kontrolleri şimdilik devre dışı bırakıldı.

## Taşınan ve korunmuş işler

- Kullanıcıya `Uygulama Tipi` ve `Yükleme Tipi` seçimi sunuldu.
- `Örnek CSV Formatı` bağlantısı çalışır halde bırakıldı.
- Açıklama alanı ve CSV dosyası yükleme formu aynı akışta korundu.
- `Gönder` sonrası iş akışı:
  - İlk tabloya (`XU_UPLOAD`) kayıt eklenmesi
  - İkinci tabloya (`XU_UPLOADDATA_V2`) kayıt eklenmesi
  - Başarılı/başarısız ekranı gösterilmesi

## Kaldırılan yapı ve kodlar

- SFTP entegrasyonları tamamıyla çıkarıldı.
- Dosya transferi, taşıma, arşivleme veya başka bir lokasyona aktarma mekanizmaları kaldırıldı.
- Login, ACL/AllowedGroups ve kurumsal yetkilendirme hatları yorum satırı veya devre dışı bırakıldı.

## Yeni proje mimarisi

- `Flask` web framework
- `Flask-SQLAlchemy` ile lokal veri saklama (SQLite)
- Servis katmanı: `services/upload_service.py`
- Veri modelleri: `models.py`
- Konfigürasyon: `config.py`
- UI şablonları: `templates/`
- Statik dosya: `static/style.css`
- Örnek CSV: `sample_data/AdslUplTempl.xlsx`

## Veri yapısı

### XU_UPLOAD
Local ortam için bir SQLAlchemy model olarak tanımlandı:
- `upload_id`
- `application_type`
- `upload_type`
- `description`
- `row_count`
- `file_name`
- `created_by`
- `created_at`

### XU_UPLOADDATA_V2
Veri yapısına uygun şekilde aşağıdaki alanlar eklendi:
- `upload_id`
- `upload_data`
- `process_file_name`
- `extra_info1` .. `extra_info10`

`process_csv_upload` servisi, CSV başlığını `upload_data` alanına kaydeder ve ekstra bilgi alanlarını upload meta verisi ile doldurur.

## Geliştirme notları

- Localde çalışacak şekilde SQLite seçildi.
- İleride Oracle veya başka bir veritabanına geçiş için SQLAlchemy katmanı kullanılmaya devam edilebilir.
- Kullanıcı doğrulaması sonrasında eklemek üzere `created_by` alanı `local-user` olarak bırakıldı.
