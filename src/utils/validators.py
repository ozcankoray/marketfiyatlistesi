# src/utils/validators.py
"""
Veri doğrulama ve sanitizasyon fonksiyonları.
"""
from typing import Dict, Any, List, Optional
from datetime import date
from src.utils.logger import logger


class ValidationError(Exception):
    """Veri doğrulama hatası için özel exception."""
    pass


def validate_product_data(product: Dict[str, Any]) -> bool:
    """
    Ürün verisinin geçerliliğini kontrol eder.
    
    Args:
        product: Kontrol edilecek ürün verisi
    
    Returns:
        True: Geçerli, False: Geçersiz
    """
    required_fields = [
        'Ürün Adı', 'Market', 'Orijinal Fiyat', 
        'TÜİK Kodu', 'Veri Tarihi'
    ]
    
    # Zorunlu alanları kontrol et
    for field in required_fields:
        if field not in product:
            logger.warning(f"Eksik alan: {field}")
            return False
        
        if product[field] is None or product[field] == '':
            logger.warning(f"Boş alan: {field}")
            return False
    
    # Fiyat kontrolü
    try:
        fiyat = float(product['Orijinal Fiyat'])
        if fiyat <= 0:
            logger.warning(f"Geçersiz fiyat: {fiyat}")
            return False
    except (ValueError, TypeError):
        logger.warning(f"Fiyat sayıya çevrilemedi: {product['Orijinal Fiyat']}")
        return False
    
    # Tarih kontrolü
    if not isinstance(product['Veri Tarihi'], date):
        logger.warning(f"Geçersiz tarih formatı: {product['Veri Tarihi']}")
        return False
    
    # Birim fiyat kontrolü (varsa)
    if product.get('Birim Fiyat') is not None:
        try:
            birim_fiyat = float(product['Birim Fiyat'])
            if birim_fiyat < 0:
                logger.warning(f"Negatif birim fiyat: {birim_fiyat}")
                return False
        except (ValueError, TypeError):
            logger.warning(f"Birim fiyat sayıya çevrilemedi: {product['Birim Fiyat']}")
            return False
    
    return True


def sanitize_product_name(name: str) -> str:
    """
    Ürün adını temizler ve normalize eder.
    
    Args:
        name: Ham ürün adı
    
    Returns:
        Temizlenmiş ürün adı
    """
    if not isinstance(name, str):
        return str(name)
    
    # Fazla boşlukları temizle
    name = ' '.join(name.split())
    
    # Özel karakterleri temizle (isteğe bağlı)
    # name = re.sub(r'[^\w\s-]', '', name)
    
    return name.strip()


def validate_and_clean_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ürün listesini doğrular ve temizler.
    
    Args:
        products: Ham ürün listesi
    
    Returns:
        Doğrulanmış ve temizlenmiş ürün listesi
    """
    cleaned_products = []
    invalid_count = 0
    
    for product in products:
        # Ürün adını temizle
        if 'Ürün Adı' in product:
            product['Ürün Adı'] = sanitize_product_name(product['Ürün Adı'])
        
        # Doğrulama
        if validate_product_data(product):
            cleaned_products.append(product)
        else:
            invalid_count += 1
    
    if invalid_count > 0:
        logger.warning(f"{invalid_count} adet geçersiz ürün veri seti atlandı")
    
    return cleaned_products


def check_duplicate_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Tekrar eden ürünleri tespit eder ve kaldırır.
    
    Args:
        products: Ürün listesi
    
    Returns:
        Tekrarsız ürün listesi
    """
    seen = set()
    unique_products = []
    duplicate_count = 0
    
    for product in products:
        # Ürün için benzersiz bir anahtar oluştur
        key = (
            product.get('Ürün Adı', ''),
            product.get('Market', ''),
            product.get('Orijinal Fiyat', 0),
            product.get('Veri Tarihi', '')
        )
        
        if key not in seen:
            seen.add(key)
            unique_products.append(product)
        else:
            duplicate_count += 1
    
    if duplicate_count > 0:
        logger.info(f"{duplicate_count} adet tekrar eden ürün kaldırıldı")
    
    return unique_products
