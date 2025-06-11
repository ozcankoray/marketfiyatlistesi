# src/api/client.py (Temizlenmiş Hali)

import requests
from typing import Optional, Dict, Any

def fetch_products_from_api(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Optional[Dict]:
    """Belirtilen API'ye POST isteği gönderir ve ürün verilerini alır."""
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[HATA] '{payload.get('keywords')}' ürünleri çekilirken bir sorun oluştu: {e}")
        return None