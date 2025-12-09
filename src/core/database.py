import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from contextlib import contextmanager
from src.utils.logger import logger

# Projenin ana dizininde 'market_data.db' adında bir veritabanı dosyası oluşturur.
DB_FILE = Path(__file__).resolve().parent.parent.parent / "market_data.db"


@contextmanager
def get_db_connection():
    """
    Context manager olarak veritabanı bağlantısı oluşturur ve yönetir.
    Otomatik olarak bağlantıyı kapatır.
    
    Yields:
        sqlite3.Connection: Veritabanı bağlantısı
    
    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Fiyatlar")
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        # Performance optimizations
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous=NORMAL")  # Balanced performance/safety
        conn.execute("PRAGMA cache_size=10000")  # Larger cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Veritabanı bağlantısı kurulamadı: {e}")
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """
    Veritabanını ve 'Fiyatlar' tablosunu (eğer yoksa) oluşturur.
    Birim fiyat normalizasyonu için yeni sütunlar eklenmiştir.
    Performans için indeksler de oluşturulur.
    """
    logger.info("Veritabanı kontrol ediliyor/oluşturuluyor...")
    
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()

            # Ana tablo oluşturma
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Fiyatlar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    urun_adi TEXT NOT NULL,
                    market TEXT NOT NULL,
                    orijinal_fiyat REAL NOT NULL,
                    birim TEXT,
                    miktar REAL,
                    birim_fiyat REAL,
                    ana_grup_adi TEXT,
                    madde_adi TEXT,
                    tuik_madde_kodu TEXT NOT NULL,
                    cekilme_tarihi DATE NOT NULL
                );
            """)

            # Performans için indeksler oluştur
            indexes = [
                ("idx_tuik_madde_kodu", "tuik_madde_kodu"),
                ("idx_market", "market"),
                ("idx_cekilme_tarihi", "cekilme_tarihi"),
                ("idx_madde_adi", "madde_adi"),
                ("idx_composite_madde_tarih", "tuik_madde_kodu, cekilme_tarihi")
            ]
            
            for index_name, columns in indexes:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name} 
                    ON Fiyatlar({columns})
                """)
                logger.debug(f"İndeks oluşturuldu/kontrol edildi: {index_name}")

            conn.commit()
            logger.info(f"✅ Veritabanı yapısı güncellendi: {DB_FILE}")
            
        except sqlite3.Error as e:
            logger.error(f"Tablo oluşturulurken bir sorun oluştu: {e}")
            raise

def insert_products_batch(products_list: List[Dict[str, Any]]):
    """
    İşlenmiş bir ürün listesini toplu olarak veritabanına kaydeder.
    Transaction ve hata yönetimi geliştirilmiş versiyon.
    
    Args:
        products_list: Kaydedilecek ürün listesi
    
    Raises:
        sqlite3.Error: Veritabanı hatası durumunda
    """
    if not products_list:
        logger.warning("Boş ürün listesi, veritabanına kayıt yapılmadı")
        return

    data_to_insert = [
        (
            product.get('Ürün Adı'),
            product.get('Market'),
            product.get('Orijinal Fiyat'),
            product.get('Birim'),
            product.get('Miktar'),
            product.get('Birim Fiyat'),
            product.get('Ana Grup Adı'),
            product.get('Madde Adı'),
            product.get('TÜİK Kodu'),
            product.get('Veri Tarihi')
        ) for product in products_list
    ]

    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            
            cursor.executemany("""
                INSERT INTO Fiyatlar (
                    urun_adi, market, orijinal_fiyat, birim, miktar, birim_fiyat,
                    ana_grup_adi, madde_adi, tuik_madde_kodu, cekilme_tarihi
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data_to_insert)

            conn.commit()
            logger.debug(f"{len(products_list)} ürün veritabanına kaydedildi")
            
        except sqlite3.Error as e:
            logger.error(f"Veri eklenirken bir sorun oluştu: {e}")
            conn.rollback()
            raise