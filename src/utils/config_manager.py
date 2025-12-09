# src/utils/config_manager.py
"""
Environment-aware configuration management.
"""
import os
from typing import Optional


class Config:
    """
    Uygulama konfigürasyonunu yöneten sınıf.
    Öncelik sırası: Environment Variables > Default Values
    """
    
    # API Configuration
    API_BASE_URL: str = os.getenv(
        "MARKET_API_BASE_URL", 
        "https://api.marketfiyati.org.tr"
    )
    API_TIMEOUT: int = int(os.getenv("MARKET_API_TIMEOUT", "15"))
    API_RATE_LIMIT: float = float(os.getenv("MARKET_API_RATE_LIMIT", "0.5"))
    
    # Retry Configuration
    MAX_RETRIES: int = int(os.getenv("MARKET_MAX_RETRIES", "3"))
    RETRY_INITIAL_DELAY: float = float(os.getenv("MARKET_RETRY_DELAY", "2.0"))
    RETRY_BACKOFF_FACTOR: float = float(os.getenv("MARKET_RETRY_BACKOFF", "2.0"))
    
    # Database Configuration
    DB_NAME: str = os.getenv("MARKET_DB_NAME", "market_data.db")
    DB_PRAGMA_WAL: bool = os.getenv("MARKET_DB_WAL", "true").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("MARKET_LOG_LEVEL", "INFO").upper()
    LOG_TO_FILE: bool = os.getenv("MARKET_LOG_TO_FILE", "true").lower() == "true"
    
    # Performance Configuration
    BATCH_SIZE: int = int(os.getenv("MARKET_BATCH_SIZE", "100"))
    
    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Konfigürasyon değeri al.
        
        Args:
            key: Konfigürasyon anahtarı
            default: Varsayılan değer
        
        Returns:
            Konfigürasyon değeri
        """
        return getattr(cls, key, default)
    
    @classmethod
    def summary(cls) -> dict:
        """
        Tüm konfigürasyon ayarlarını döndürür.
        
        Returns:
            Konfigürasyon dictionary'si
        """
        return {
            key: value
            for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }


# Global config instance
config = Config()
