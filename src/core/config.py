# src/core/config.py

# İki farklı API uç noktasını da tanımlıyoruz
CATEGORY_SEARCH_URL = "https://api.marketfiyati.org.tr/api/v2/searchByCategories"
GENERAL_SEARCH_URL = "https://api.marketfiyati.org.tr/api/v2/search"

# Her iki istek için de kullanılabilecek ortak ve gerçekçi başlıklar
HEADERS = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'origin': 'https://marketfiyati.org.tr',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

# --- PAYLOAD OLUŞTURMA FONKSİYONLARI ---

def get_category_payload(category_name: str, page: int) -> dict:
    """
    Kategoriye özel, temiz veri çekmek için payload oluşturur.
    'searchByCategories' uç noktası ile kullanılır.
    """
    return {
        "keywords": category_name,
        "pages": page,
        "size": 50,
        "menuCategory": False,
        "latitude": 41.0645117635181,
        "longitude": 28.9775156063165,
        "distance": 10,
        # depots listesini şimdilik genel tutmak için kaldırıyoruz,
        # sorun yaşarsak geri ekleyebiliriz.
        # "depots": [...]
    }

def get_general_search_payload(search_term: str, page: int) -> dict:
    """
    Genel arama yapmak için payload oluşturur.
    'search' uç noktası ile kullanılır.
    """
    return {
        "keywords": search_term,
        "pages": page,
        "size": 50,
        "latitude": 41.0645117635181,
        "longitude": 28.9775156063165,
        "distance": 10,
    }