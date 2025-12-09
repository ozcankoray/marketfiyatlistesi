# Market Fiyat Listesi - Kullanım Rehberi

## 📖 İçindekiler
1. [Hızlı Başlangıç](#hızlı-başlangıç)
2. [Kurulum](#kurulum)
3. [Temel Kullanım](#temel-kullanım)
4. [İleri Düzey Özellikler](#ileri-düzey-özellikler)
5. [Konfigürasyon](#konfigürasyon)
6. [Analiz ve Raporlama](#analiz-ve-raporlama)
7. [Sorun Giderme](#sorun-giderme)

---

## 🚀 Hızlı Başlangıç

### Minimum Gereksinimler
- Python 3.8 veya üzeri
- Internet bağlantısı
- ~500 MB boş disk alanı

### 3 Adımda Başlat
```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. Programı çalıştır
python main.py

# 3. Sonuçları kontrol et
# Veritabanı: market_data.db
# Loglar: logs/scraper_YYYYMMDD.log
```

---

## 📦 Kurulum

### Adım 1: Depoyu Klonlayın
```bash
git clone https://github.com/ozcankoray/marketfiyatlistesi.git
cd marketfiyatlistesi
```

### Adım 2: Virtual Environment Oluşturun (Önerilen)
```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: İlk Çalıştırma
```bash
python main.py
```

---

## 💡 Temel Kullanım

### Ana Program
```bash
python main.py
```

**Ne yapar?**
- TÜİK gıda sepetindeki tüm maddeleri tarar
- Her madde için API'den fiyat verilerini çeker
- Verileri filtreler ve işler
- SQLite veritabanına kaydeder
- Özet rapor üretir

**Örnek Çıktı:**
```
2024-12-09 12:00:00 - market_scraper - INFO - 🚀 Program Başlatılıyor...
2024-12-09 12:00:01 - market_scraper - INFO - ✅ Veritabanı yapısı güncellendi
2024-12-09 12:00:02 - market_scraper - INFO - (1/150) İşlenen Madde: 'Pirinç'
...
2024-12-09 12:15:30 - market_scraper - INFO - 🎉 TÜM İŞLEMLER TAMAMLANDI 🎉
2024-12-09 12:15:30 - market_scraper - INFO - -> Toplam 5,432 adet ürün verisi aktarıldı
```

### Veritabanı Sorgulama

**Python ile:**
```python
import sqlite3
conn = sqlite3.connect('market_data.db')
cursor = conn.cursor()

# En ucuz 10 ürünü getir
cursor.execute("""
    SELECT urun_adi, market, birim_fiyat 
    FROM Fiyatlar 
    WHERE madde_adi = 'Süt' 
    ORDER BY birim_fiyat ASC 
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row[0]} - {row[1]}: ₺{row[2]:.2f}/litre")

conn.close()
```

**SQL ile:**
```bash
sqlite3 market_data.db

# En çok ürün satan marketler
SELECT market, COUNT(*) as urun_sayisi 
FROM Fiyatlar 
GROUP BY market 
ORDER BY urun_sayisi DESC 
LIMIT 5;
```

---

## 🎯 İleri Düzey Özellikler

### 1. İstatistiksel Analiz

#### Python Script ile:
```python
from src.analytics.statistics import PriceAnalytics

# Veritabanı özeti
summary = PriceAnalytics.get_database_summary()
print(f"Toplam Ürün: {summary['toplam_urun_sayisi']:,}")
print(f"Ortalama Fiyat: ₺{summary['ortalama_fiyat']}")

# Süt için istatistikler
stats = PriceAnalytics.get_price_statistics_by_item("Süt")
print(f"Min: ₺{stats['min_birim_fiyat']}/lt")
print(f"Max: ₺{stats['max_birim_fiyat']}/lt")
print(f"Ortalama: ₺{stats['ortalama_birim_fiyat']}/lt")

# En ucuz 5 süt ürünü
ucuz_sutler = PriceAnalytics.get_cheapest_products("Süt", limit=5)
for urun in ucuz_sutler:
    print(f"{urun['urun_adi']} - {urun['market']}: ₺{urun['birim_fiyat']}/lt")
```

#### Market Karşılaştırması:
```python
# Hangi market süt için en ucuz?
karsilastirma = PriceAnalytics.get_market_comparison("Süt")
for market in karsilastirma:
    print(f"{market['market']}: ₺{market['ortalama_birim_fiyat']}/lt")
```

#### Fiyat Trendleri:
```python
# Son 30 günün trend analizi
trendler = PriceAnalytics.get_price_trends("Ekmek", days=30)
for trend in trendler:
    print(f"{trend['tarih']}: ₺{trend['ortalama_birim_fiyat']}")
```

### 2. Log İnceleme

Loglar `logs/` dizininde otomatik olarak tutulur:

```bash
# Bugünün logunu görüntüle
cat logs/scraper_20241209.log

# Sadece hataları göster
grep ERROR logs/scraper_20241209.log

# Canlı takip (program çalışırken)
tail -f logs/scraper_20241209.log

# Son 100 satır
tail -n 100 logs/scraper_20241209.log
```

### 3. Özel Filtreleme

TÜİK sepetini özelleştirmek için `src/core/tuik_sepeti.py` dosyasını düzenleyin:

```python
# Sadece belirli maddeleri çekmek için
TUIK_GIDA_SEPETI = [
    {
        "ana_grup_adi": "Süt, Peynir ve Yumurta",
        "madde_kodu": "0114101",
        "madde_adi": "Süt",
        "api_kategori_adi": "Süt",
        "onay_kelimeleri": ["süt"],
        "yasakli_kelimeler": ["yoğurt", "peynir", "kefir"]
    },
    # Diğer maddeler...
]
```

---

## ⚙️ Konfigürasyon

### Environment Variables

Programı çalıştırmadan önce environment variables ile özelleştirebilirsiniz:

```bash
# API ayarları
export MARKET_API_TIMEOUT=30          # Varsayılan: 15 saniye
export MARKET_API_RATE_LIMIT=1.0     # Varsayılan: 0.5 saniye

# Retry ayarları
export MARKET_MAX_RETRIES=5           # Varsayılan: 3
export MARKET_RETRY_DELAY=3.0         # Varsayılan: 2.0 saniye
export MARKET_RETRY_BACKOFF=2.5       # Varsayılan: 2.0

# Log ayarları
export MARKET_LOG_LEVEL=DEBUG         # Varsayılan: INFO
export MARKET_LOG_TO_FILE=true        # Varsayılan: true

# Veritabanı ayarları
export MARKET_DB_NAME=fiyatlar.db     # Varsayılan: market_data.db

# Sonra çalıştır
python main.py
```

### Linux/Mac için .env Dosyası

`.env` dosyası oluşturun:
```bash
MARKET_API_TIMEOUT=30
MARKET_MAX_RETRIES=5
MARKET_LOG_LEVEL=DEBUG
```

Sonra:
```bash
# .env dosyasını yükle
export $(cat .env | xargs)
python main.py
```

### Windows için

PowerShell:
```powershell
$env:MARKET_API_TIMEOUT = "30"
$env:MARKET_MAX_RETRIES = "5"
python main.py
```

---

## 📊 Analiz ve Raporlama

### Özet Rapor

Program sonunda otomatik olarak bir özet rapor üretilir:

```
==============================================================
📊 VERİTABANI ÖZET RAPORU
==============================================================
Toplam Ürün Sayısı: 5,432
Benzersiz Market Sayısı: 8
Benzersiz Madde Sayısı: 145
İlk Veri Tarihi: 2024-12-09
Son Veri Tarihi: 2024-12-09
Ortalama Fiyat: ₺45.32
==============================================================
```

### Excel Export (Varsa)

```python
from src.exporters.to_excel import export_to_excel

# Tüm verileri Excel'e aktar
export_to_excel(
    output_file="fiyat_raporu.xlsx",
    madde_adi="Süt"  # Opsiyonel: Sadece belirli madde
)
```

### Pandas ile Analiz

```python
import sqlite3
import pandas as pd

# Veritabanından DataFrame oluştur
conn = sqlite3.connect('market_data.db')
df = pd.read_sql_query("SELECT * FROM Fiyatlar", conn)

# Temel istatistikler
print(df.describe())

# Market bazlı ortalama fiyatlar
market_avg = df.groupby('market')['birim_fiyat'].mean()
print(market_avg.sort_values())

# Madde bazlı fiyat dağılımı
df.boxplot(column='birim_fiyat', by='madde_adi', figsize=(15, 8))

conn.close()
```

---

## 🔧 Sorun Giderme

### Problem 1: "ModuleNotFoundError"
```
ModuleNotFoundError: No module named 'requests'
```

**Çözüm:**
```bash
pip install -r requirements.txt
```

### Problem 2: "Database is locked"
```
sqlite3.OperationalError: database is locked
```

**Çözüm:**
- Başka bir program veritabanını kullanıyor olabilir
- Veritabanını kapatın veya programı tekrar çalıştırın

### Problem 3: "Connection timeout"
```
requests.exceptions.Timeout: HTTPConnectionPool
```

**Çözüm:**
```bash
# Timeout süresini artırın
export MARKET_API_TIMEOUT=60
python main.py
```

### Problem 4: "Too many requests / Rate limit"
```
HTTP 429 Too Many Requests
```

**Çözüm:**
```bash
# Bekleme süresini artırın
export MARKET_API_RATE_LIMIT=2.0
python main.py
```

### Problem 5: Log Dosyası Çok Büyük

```bash
# Eski logları temizle
rm logs/scraper_*.log

# Veya sadece 7 günden eskileri sil
find logs/ -name "scraper_*.log" -mtime +7 -delete
```

### Problem 6: Veritabanı Çok Büyük

```bash
# Eski verileri sil
sqlite3 market_data.db "DELETE FROM Fiyatlar WHERE cekilme_tarihi < date('now', '-30 days')"

# Veritabanını optimize et
sqlite3 market_data.db "VACUUM"
```

---

## 🎓 En İyi Uygulamalar

### 1. Düzenli Çalıştırma

Cron job ile otomatik çalıştırma (Linux/Mac):
```bash
# Crontab düzenle
crontab -e

# Her gün saat 03:00'te çalıştır
0 3 * * * cd /path/to/marketfiyatlistesi && /path/to/venv/bin/python main.py
```

Windows Task Scheduler ile:
- Task Scheduler'ı aç
- "Create Basic Task" seç
- Trigger: Daily
- Action: Start a program
- Program: `C:\path\to\python.exe`
- Arguments: `C:\path\to\marketfiyatlistesi\main.py`

### 2. Backup Stratejisi

```bash
# Günlük backup
cp market_data.db backups/market_data_$(date +%Y%m%d).db

# Eski backupları temizle (30 günden eski)
find backups/ -name "market_data_*.db" -mtime +30 -delete
```

### 3. Monitoring

```python
# monitoring.py
from src.analytics.statistics import PriceAnalytics
import smtplib
from email.mime.text import MIMEText

def send_alert(message):
    """E-posta bildirimi gönder."""
    msg = MIMEText(message)
    msg['Subject'] = 'Market Fiyat Raporu'
    msg['From'] = 'sender@example.com'
    msg['To'] = 'receiver@example.com'
    
    # SMTP ayarlarınızı yapılandırın
    # ...

# Günlük rapor gönder
summary = PriceAnalytics.get_database_summary()
send_alert(f"Bugün {summary['toplam_urun_sayisi']} ürün toplandı")
```

---

## 📞 Destek

### Yardım Kaynakları

1. **README.md**: Genel bilgiler
2. **ANALIZ_VE_OPTIMIZASYON.md**: Teknik detaylar
3. **Bu dosya**: Kullanım rehberi
4. **GitHub Issues**: Bug raporu ve özellik istekleri

### İletişim

- GitHub: [@ozcankoray](https://github.com/ozcankoray)
- Issues: [GitHub Issues](https://github.com/ozcankoray/marketfiyatlistesi/issues)

---

## 🎉 Sonuç

Bu rehber ile Market Fiyat Listesi projesini etkili şekilde kullanabilirsiniz:

✅ Otomatik veri toplama
✅ Güvenilir çalışma (retry, logging)
✅ Kapsamlı analiz imkanları
✅ Kolay konfigürasyon
✅ Sorun giderme

**İyi kullanımlar!** 🚀

---

**Son Güncelleme**: 2024-12-09  
**Versiyon**: 2.0
