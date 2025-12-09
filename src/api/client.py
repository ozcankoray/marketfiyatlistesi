# src/api/client.py (Geliştirilmiş Versiyon)

import requests
import time
from typing import Optional, Dict, Any
from src.utils.logger import logger
from src.utils.retry import retry_with_backoff


class RateLimiter:
    """
    API rate limiting için basit bir sınıf.
    Son istek zamanını takip eder ve minimum bekleme süresini zorlar.
    """
    def __init__(self, min_delay: float = 0.5):
        self.min_delay = min_delay
        self.last_request_time = 0.0
    
    def wait_if_needed(self):
        """Gerekirse rate limit için bekle."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed
            logger.debug(f"Rate limiting: {sleep_time:.2f} saniye bekleniyor...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


# Global rate limiter instance
rate_limiter = RateLimiter(min_delay=0.5)


@retry_with_backoff(
    max_retries=3,
    initial_delay=2.0,
    backoff_factor=2.0,
    exceptions=(requests.exceptions.RequestException,)
)
def fetch_products_from_api(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Optional[Dict]:
    """
    API'den ürün verilerini çeker. Retry ve rate limiting ile geliştirilmiş versiyon.
    
    Args:
        url: API endpoint URL'i
        headers: HTTP başlıkları
        payload: POST isteği için payload
    
    Returns:
        API yanıtı (JSON dict) veya hata durumunda None
    
    Raises:
        requests.exceptions.RequestException: Maksimum retry sayısından sonra
    """
    # Rate limiting uygula
    rate_limiter.wait_if_needed()
    
    try:
        logger.debug(f"API isteği gönderiliyor: {payload.get('keywords', 'N/A')}")
        
        response = requests.post(
            url, 
            headers=headers, 
            json=payload, 
            timeout=15
        )
        response.raise_for_status()
        
        data = response.json()
        logger.debug(
            f"API yanıtı alındı: {len(data.get('content', []))} ürün (Sayfa: {payload.get('pages', 0)})"
        )
        
        return data
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout hatası: '{payload.get('keywords')}' için istek zaman aşımına uğradı")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP hatası {e.response.status_code}: '{payload.get('keywords')}' - {str(e)}")
        raise
    except requests.exceptions.ConnectionError:
        logger.error(f"Bağlantı hatası: '{payload.get('keywords')}' için bağlantı kurulamadı")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"API isteği başarısız: '{payload.get('keywords')}' - {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Beklenmeyen hata: '{payload.get('keywords')}' - {type(e).__name__}: {str(e)}")
        return None