# src/utils/retry.py
"""
Retry decorator with exponential backoff for robust API calls.
"""
import time
import functools
from typing import Callable, Type, Tuple
from src.utils.logger import logger


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Exponential backoff ile retry dekoratörü.
    
    Args:
        max_retries: Maksimum deneme sayısı
        initial_delay: İlk bekleme süresi (saniye)
        backoff_factor: Her denemede bekleme süresinin çarpanı
        exceptions: Yakalanacak exception türleri
    
    Returns:
        Dekoratör fonksiyonu
    
    Example:
        @retry_with_backoff(max_retries=3, initial_delay=1.0)
        def risky_api_call():
            # API call code
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"'{func.__name__}' fonksiyonu {max_retries} denemeden sonra başarısız oldu. "
                            f"Son hata: {str(e)}"
                        )
                        raise
                    
                    logger.warning(
                        f"'{func.__name__}' başarısız oldu (Deneme {attempt + 1}/{max_retries}). "
                        f"Hata: {str(e)}. {delay:.1f} saniye sonra tekrar denenecek..."
                    )
                    
                    time.sleep(delay)
                    delay *= backoff_factor
            
            # Bu noktaya normalde ulaşılmamalı, ama güvenlik için
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator
