# src/utils/logger.py
"""
Centralized logging configuration for the application.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "market_scraper", log_level: int = logging.INFO) -> logging.Logger:
    """
    Merkezi loglama sistemi kurulumu.
    
    Args:
        name: Logger adı
        log_level: Loglama seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Yapılandırılmış logger objesi
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Birden fazla handler eklenmesini önle
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # File handler - logs dizini oluştur
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"scraper_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()
