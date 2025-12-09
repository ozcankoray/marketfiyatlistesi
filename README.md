# Market Fiyat Listesi - Web Scraping Projesi

## 📋 Proje Hakkında

Bu proje, Türkiye'deki online market fiyatlarını otomatik olarak toplayan, işleyen ve veritabanına kaydeden bir Python uygulamasıdır. TÜİK (Türkiye İstatistik Kurumu) gıda sepetindeki ürünlerin fiyat verilerini periyodik olarak çekerek, fiyat takibi ve analiz imkanı sağlar.

## 🚀 Özellikler

- **Otomatik Veri Toplama**: Market Fiyatı API'sinden ürün bilgilerini otomatik olarak çeker
- **Akıllı Filtreleme**: TÜİK sepetine göre özelleştirilmiş filtreleme mekanizması
- **Birim Fiyat Hesaplama**: Farklı gramaj/hacimlerdeki ürünleri karşılaştırılabilir hale getirir
- **SQLite Veritabanı**: Verileri yerel veritabanında saklar ve yönetir
- **Toplu İşlem**: Batch insert ile veritabanı performansını optimize eder

## 📁 Proje Yapısı

```
marketfiyatlistesi/
│
├── main.py                     # Ana uygulama giriş noktası
├── requirements.txt            # Python bağımlılıkları
├── market_data.db             # SQLite veritabanı (otomatik oluşturulur)
│
├── src/
│   ├── api/
│   │   └── client.py          # API istek yönetimi
│   │
│   ├── core/
│   │   ├── config.py          # Konfigürasyon ayarları
│   │   ├── database.py        # Veritabanı işlemleri
│   │   ├── tuik_sepeti.py     # TÜİK gıda sepeti tanımları
│   │   └── mappings.py        # Veri eşleştirmeleri
│   │
│   ├── parsers/
│   │   ├── product_parser.py  # Ürün veri ayrıştırıcı
│   │   └── category_parser.py # Kategori ayrıştırıcı
│   │
│   ├── exporters/
│   │   └── to_excel.py        # Excel export fonksiyonları
│   │
│   └── ui/
│       └── display.py         # Kullanıcı arayüzü fonksiyonları
│
└── calculate_index.py         # Fiyat endeksi hesaplama modülü
```

## 🔧 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip paket yöneticisi

### Adımlar

1. Projeyi klonlayın:
```bash
git clone https://github.com/ozcankoray/marketfiyatlistesi.git
cd marketfiyatlistesi
```

2. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı çalıştırın:
```bash
python main.py
```

## 📊 Kullanım

### Temel Kullanım

```bash
# Ana veri toplama işlemini başlatır
python main.py

# Excel formatında veri çıktısı almak için
python src/exporters/to_excel.py

# Fiyat endeksi hesaplama
python calculate_index.py
```

### Veritabanı Yapısı

**Fiyatlar Tablosu**:
- `id`: Otomatik artan birincil anahtar
- `urun_adi`: Ürün adı
- `market`: Market adı
- `orijinal_fiyat`: Ürünün liste fiyatı
- `birim`: Ölçü birimi (gr, ml, adet)
- `miktar`: Ürün miktarı
- `birim_fiyat`: Normalize edilmiş birim fiyat (kg/litre bazında)
- `ana_grup_adi`: TÜİK ana grup kategorisi
- `madde_adi`: TÜİK madde adı
- `tuik_madde_kodu`: TÜİK standart kodu
- `cekilme_tarihi`: Veri toplama tarihi

## 🔍 Kod Akışı

1. **Başlatma**: `main.py` uygulamayı başlatır
2. **Veritabanı Hazırlık**: `init_db()` gerekli tabloları oluşturur
3. **TÜİK Sepeti Tarama**: Her madde için döngü başlar
4. **API Sorgusu**: Kategori bazlı sayfalama ile veri çekilir
5. **Veri Filtreleme**: Onay/yasaklı kelimeler ile filtreleme
6. **Birim Hesaplama**: Gramaj/hacim çıkarma ve birim fiyat hesaplama
7. **Veritabanı Kayıt**: Batch insert ile toplu kayıt

## 🛠️ Teknik Detaylar

### API İletişimi

Proje, `https://api.marketfiyati.org.tr` API'sini kullanır:
- **Endpoint**: `/api/v2/searchByCategories`
- **Method**: POST
- **Sayfalama**: 50 ürün/sayfa
- **Rate Limit**: 0.5 saniye bekleme (şu anki implementasyon)

### Birim Fiyat Normalizasyonu

Farklı gramaj/hacimlerdeki ürünleri karşılaştırmak için:
- Gram bazlı ürünler → kg fiyatına çevrilir
- ML bazlı ürünler → litre fiyatına çevrilir
- Çarpım formatları (6x200ml) → toplam miktar hesaplanır

### Filtreleme Stratejisi

Her TÜİK maddesi için:
- **Onay Kelimeleri**: Ürün adında bulunması gereken kelimeler
- **Yasaklı Kelimeler**: Ürün adında bulunmaması gereken kelimeler

## 📈 Performans

Mevcut implementasyon:
- ~150 TÜİK maddesi
- Senkron HTTP istekleri
- Ortalama süre: ~10-15 dakika (ağ hızına bağlı)
- Batch insert ile optimize edilmiş veritabanı yazma

## ⚠️ Önemli Notlar

### Yasal ve Etik Kullanım

- Bu proje, halka açık bir API kullanmaktadır
- Veri toplama işlemi makul rate limiting ile yapılmaktadır
- Kullanıcılar, yerel yasalar ve API kullanım koşullarına uymakla yükümlüdür
- Ticari kullanım öncesinde API sağlayıcısından izin alınmalıdır

### Sınırlamalar

- IP bloklama riski (agresif kullanımda)
- API değişikliklerine karşı kırılganlık
- Tek thread çalışma (gelecekte async geliştirme planlanıyor)
- Internet bağlantısına tam bağımlılık

## 🔮 Gelecek Geliştirmeler

- [ ] Asenkron HTTP istekleri (asyncio + aiohttp)
- [ ] Proxy rotation desteği
- [ ] Exponential backoff retry mekanizması
- [ ] Comprehensive logging sistemi
- [ ] Veritabanı indeksleme optimizasyonu
- [ ] Redis caching katmanı
- [ ] Real-time monitoring ve alerting
- [ ] Docker containerization
- [ ] Unit ve integration testler
- [ ] CI/CD pipeline

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📝 Lisans

Bu proje açık kaynaklıdır ve eğitim amaçlı geliştirilmiştir.

## 📧 İletişim

Proje Sahibi: Özcan Koray
GitHub: [@ozcankoray](https://github.com/ozcankoray)

---

**Not**: Bu dokümantasyon, projenin mevcut durumunu yansıtmaktadır. Gelecek güncellemelerle birlikte değişiklik gösterebilir.
