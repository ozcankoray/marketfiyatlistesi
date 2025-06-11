# src/core/config.py (Nihai ve Doğru Market Listesi ile)

"""
Uygulamanın konfigürasyon ayarlarını ve sabitlerini barındırır.
Kategori yapısı artık API'den değil, buradan statik olarak okunur.
"""

# API Adresleri
SEARCH_API_URL = "https://api.marketfiyati.org.tr/api/v2/searchByCategories"

# API isteği için gönderilecek HTTP başlıkları
HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# SİZİN TARAFINIZDAN SAĞLANAN KESİN DOĞRU KATEGORİ YAPISI
CATEGORY_STRUCTURE = {
    "Meyve ve Sebze": ["Meyve", "Sebze"],
    "Et, Tavuk ve Balık": ["Kırmızı Et", "Beyaz Et", "Deniz Ürünleri", "Şarküteri", "Sakatat"],
    "Süt Ürünleri ve Kahvaltılık": ["Süt", "Yumurta", "Peynir", "Yoğurt", "Zeytin", "Tereyağı ve Margarin", "Sürülebilir Ürünler ve Kahvaltılık Soslar", "Helva Tahin ve Pekmez", "Bal ve Reçel", "Kahvaltılık Gevrek Bar ve Granola", "Kaymak ve Krema"],
    "Temel Gıda": ["Ekmek ve Unlu Mamüller", "Sıvı Yağlar", "Bakliyat", "Şeker ve Tatlandırıcılar", "Pasta Malzemeleri", "Un ve İrmik", "Mantı Makarna ve Erişte", "Ketçap Mayonez Sos ve Sirkeler", "Tuz Baharat ve Harçlar", "Salça", "Turşu", "Konserve", "Hazır Gıda", "Bebek Mamaları"],
    "İçecek": ["Su", "Meyve Suyu", "Gazlı İçecekler", "Gazsız İçecekler", "Ayran ve Kefir", "Maden Suyu", "Çay ve Bitki Çayları", "Kahve"],
    "Atıştırmalık ve Tatlı": ["Çikolata", "Gofret", "Bisküvi ve Kraker", "Kek", "Cips", "Kuruyemiş ve Kuru Meyve", "Sakız ve Şekerleme", "Tatlılar", "Dondurmalar"],
    "Temizlik ve Kişisel Bakım Ürünleri": ["Bulaşık Temizlik Ürünleri", "Çamaşır Temizlik Ürünleri", "Genel Temizlik Ürünleri", "Mutfak Sarf Malzemeleri", "Tuvalet Kağıdı", "Kağıt Havlu", "Kağıt Peçete ve Mendil", "Islak Mendil", "Saç Bakım", "Duş Banyo ve Sabun", "Ağız Bakım", "Hijyenik Ped", "Bebek ve Hasta Bezi", "Parfüm Deodorant Kolonya ve Kokular", "Cilt Bakımı", "Makyaj", "Diğer Temizlik ve Kişisel Bakım Ürünleri"]
}

def get_payload(keyword: str, page: int, is_menu_category: bool) -> dict:
    """Dinamik olarak arama kriteri (payload) oluşturur."""
    return {
        "keywords": keyword,
        "pages": page,
        "size": 50, # Bu değeri 50'de tutabiliriz, API zaten kendi sınırını uyguluyor.
        "menuCategory": is_menu_category,
        "latitude": 41.0645117635181,
        "longitude": 28.9775156063165,
        "distance": 10,
        # EN ÖNEMLİ GÜNCELLEME: Sizin sağladığınız tam market listesi
        "depots": [
            "a101-I017", "bim-J057", "sok-7399", "sok-6504", "bim-L518",
            "a101-8674", "a101-E055", "sok-10531", "tarim_kredi-5500",
            "bim-J065", "carrefour-3476", "sok-10775", "bim-J618",
            "sok-10702", "a101-J217", "a101-8168", "bim-J056", "migros-656",
            "migros-7792", "migros-5157", "tarim_kredi-5373", "migros-8122",
            "carrefour-5024", "carrefour-3222", "migros-3301", "carrefour-3585",
            "carrefour-2016", "tarim_kredi-5499", "tarim_kredi-5372",
            "tarim_kredi-5109", "hakmar-5521", "hakmar-5770", "hakmar-5602",
            "hakmar-5200", "hakmar-5113"
        ]
    }