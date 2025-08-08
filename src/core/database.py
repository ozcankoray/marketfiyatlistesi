import sqlite3
from pathlib import Path
from typing import Dict, Any, List

# Projenin ana dizininde 'market_data.db' adında bir veritabanı dosyası oluşturur.
DB_FILE = Path(__file__).resolve().parent.parent.parent / "market_data.db"

def get_db_connection():
    """Veritabanı bağlantısı oluşturur ve döndürür."""
    try:
        conn = sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"[HATA] Veritabanı bağlantısı kurulamadı: {e}")
        return None

def init_db():
    """
    Veritabanını ve 'Fiyatlar' tablosunu (eğer yoksa) oluşturur.
    Birim fiyat normalizasyonu için yeni sütunlar eklenmiştir.
    """
    print("Veritabanı kontrol ediliyor/oluşturuluyor...")
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

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

        conn.commit()
        print(f"✅ Veritabanı yapısı güncellendi: {DB_FILE}")
    except sqlite3.Error as e:
        print(f"[HATA] Tablo oluşturulurken bir sorun oluştu: {e}")
    finally:
        if conn:
            conn.close()

def insert_products_batch(products_list: List[Dict[str, Any]]):
    """
    İşlenmiş bir ürün listesini toplu olarak veritabanına kaydeder.
    """
    if not products_list:
        return

    conn = get_db_connection()
    if conn is None:
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

    try:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO Fiyatlar (
                urun_adi, market, orijinal_fiyat, birim, miktar, birim_fiyat,
                ana_grup_adi, madde_adi, tuik_madde_kodu, cekilme_tarihi
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data_to_insert)

        conn.commit()
    except sqlite3.Error as e:
        print(f"[HATA] Veri eklenirken bir sorun oluştu: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()