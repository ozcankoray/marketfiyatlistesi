# src/analytics/statistics.py
"""
Veritabanındaki fiyat verilerini analiz eden ve istatistikler üreten modül.
"""
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from src.core.database import get_db_connection
from src.utils.logger import logger


class PriceAnalytics:
    """Fiyat analizi ve istatistik sınıfı."""
    
    @staticmethod
    def get_database_summary() -> Dict[str, Any]:
        """
        Veritabanının genel özetini döndürür.
        
        Returns:
            İstatistikler içeren dictionary
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Toplam ürün sayısı
            cursor.execute("SELECT COUNT(*) FROM Fiyatlar")
            total_products = cursor.fetchone()[0]
            
            # Benzersiz market sayısı
            cursor.execute("SELECT COUNT(DISTINCT market) FROM Fiyatlar")
            unique_markets = cursor.fetchone()[0]
            
            # Benzersiz madde sayısı
            cursor.execute("SELECT COUNT(DISTINCT madde_adi) FROM Fiyatlar")
            unique_items = cursor.fetchone()[0]
            
            # Tarih aralığı
            cursor.execute("SELECT MIN(cekilme_tarihi), MAX(cekilme_tarihi) FROM Fiyatlar")
            date_range = cursor.fetchone()
            
            # Ortalama fiyat
            cursor.execute("SELECT AVG(orijinal_fiyat) FROM Fiyatlar WHERE orijinal_fiyat > 0")
            avg_price = cursor.fetchone()[0]
            
            return {
                'toplam_urun_sayisi': total_products,
                'benzersiz_market_sayisi': unique_markets,
                'benzersiz_madde_sayisi': unique_items,
                'ilk_veri_tarihi': date_range[0] if date_range else None,
                'son_veri_tarihi': date_range[1] if date_range else None,
                'ortalama_fiyat': round(avg_price, 2) if avg_price else 0
            }
    
    @staticmethod
    def get_price_statistics_by_item(madde_adi: str) -> Dict[str, Any]:
        """
        Belirli bir madde için fiyat istatistikleri.
        
        Args:
            madde_adi: TÜİK madde adı
        
        Returns:
            İstatistikler içeren dictionary
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as urun_sayisi,
                    MIN(birim_fiyat) as min_birim_fiyat,
                    MAX(birim_fiyat) as max_birim_fiyat,
                    AVG(birim_fiyat) as ortalama_birim_fiyat,
                    COUNT(DISTINCT market) as market_sayisi
                FROM Fiyatlar
                WHERE madde_adi = ? AND birim_fiyat IS NOT NULL
            """, (madde_adi,))
            
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                return {
                    'madde_adi': madde_adi,
                    'urun_sayisi': result[0],
                    'min_birim_fiyat': round(result[1], 2) if result[1] else None,
                    'max_birim_fiyat': round(result[2], 2) if result[2] else None,
                    'ortalama_birim_fiyat': round(result[3], 2) if result[3] else None,
                    'market_sayisi': result[4]
                }
            
            return {'madde_adi': madde_adi, 'urun_sayisi': 0}
    
    @staticmethod
    def get_cheapest_products(madde_adi: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Belirli bir madde için en ucuz ürünleri döndürür.
        
        Args:
            madde_adi: TÜİK madde adı
            limit: Döndürülecek ürün sayısı
        
        Returns:
            Ürün listesi
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    urun_adi,
                    market,
                    orijinal_fiyat,
                    birim,
                    miktar,
                    birim_fiyat,
                    cekilme_tarihi
                FROM Fiyatlar
                WHERE madde_adi = ? AND birim_fiyat IS NOT NULL
                ORDER BY birim_fiyat ASC
                LIMIT ?
            """, (madde_adi, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'urun_adi': row[0],
                    'market': row[1],
                    'orijinal_fiyat': round(row[2], 2),
                    'birim': row[3],
                    'miktar': row[4],
                    'birim_fiyat': round(row[5], 2) if row[5] else None,
                    'veri_tarihi': row[6]
                })
            
            return results
    
    @staticmethod
    def get_market_comparison(madde_adi: str) -> List[Dict[str, Any]]:
        """
        Farklı marketlerin belirli bir madde için ortalama fiyatlarını karşılaştırır.
        
        Args:
            madde_adi: TÜİK madde adı
        
        Returns:
            Market karşılaştırma listesi
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    market,
                    COUNT(*) as urun_sayisi,
                    AVG(birim_fiyat) as ortalama_birim_fiyat,
                    MIN(birim_fiyat) as min_birim_fiyat,
                    MAX(birim_fiyat) as max_birim_fiyat
                FROM Fiyatlar
                WHERE madde_adi = ? AND birim_fiyat IS NOT NULL
                GROUP BY market
                ORDER BY ortalama_birim_fiyat ASC
            """, (madde_adi,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'market': row[0],
                    'urun_sayisi': row[1],
                    'ortalama_birim_fiyat': round(row[2], 2) if row[2] else None,
                    'min_birim_fiyat': round(row[3], 2) if row[3] else None,
                    'max_birim_fiyat': round(row[4], 2) if row[4] else None
                })
            
            return results
    
    @staticmethod
    def get_price_trends(madde_adi: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Belirli bir madde için son N günün fiyat trendini döndürür.
        
        Args:
            madde_adi: TÜİK madde adı
            days: Kaç günlük veri
        
        Returns:
            Günlük ortalama fiyatlar
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            cursor.execute("""
                SELECT 
                    cekilme_tarihi,
                    AVG(birim_fiyat) as ortalama_birim_fiyat,
                    COUNT(*) as urun_sayisi
                FROM Fiyatlar
                WHERE madde_adi = ? 
                    AND birim_fiyat IS NOT NULL
                    AND cekilme_tarihi BETWEEN ? AND ?
                GROUP BY cekilme_tarihi
                ORDER BY cekilme_tarihi ASC
            """, (madde_adi, start_date, end_date))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'tarih': row[0],
                    'ortalama_birim_fiyat': round(row[1], 2) if row[1] else None,
                    'urun_sayisi': row[2]
                })
            
            return results
    
    @staticmethod
    def print_summary_report():
        """Veritabanının genel özetini konsola yazdırır."""
        try:
            summary = PriceAnalytics.get_database_summary()
            
            logger.info("\n" + "=" * 60)
            logger.info("📊 VERİTABANI ÖZET RAPORU")
            logger.info("=" * 60)
            logger.info(f"Toplam Ürün Sayısı: {summary['toplam_urun_sayisi']:,}")
            logger.info(f"Benzersiz Market Sayısı: {summary['benzersiz_market_sayisi']}")
            logger.info(f"Benzersiz Madde Sayısı: {summary['benzersiz_madde_sayisi']}")
            logger.info(f"İlk Veri Tarihi: {summary['ilk_veri_tarihi']}")
            logger.info(f"Son Veri Tarihi: {summary['son_veri_tarihi']}")
            logger.info(f"Ortalama Fiyat: ₺{summary['ortalama_fiyat']}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Özet raporu oluşturulurken hata: {e}")
