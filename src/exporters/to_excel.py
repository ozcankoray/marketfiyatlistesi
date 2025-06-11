# src/exporters/to_excel.py (İndirilenler Klasörüne Kaydetme Eklendi)

"""
İşlenmiş veriyi Excel dosyasına aktarmaktan sorumlu fonksiyonları içerir.
Dosyayı otomatik olarak kullanıcının İndirilenler klasörüne kaydeder.
"""
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path  # Modern yol işlemleri için pathlib kütüphanesini import ediyoruz


def save_to_excel(products: List[Dict[str, Any]], filename: str = "market_fiyatlari.xlsx"):
    """
    Verilen ürün listesini bir pandas DataFrame'e dönüştürür ve kullanıcının
    İndirilenler klasörüne kaydeder.

    Args:
        products (List[Dict]): Kaydedilecek ürünlerin listesi.
        filename (str): Oluşturulacak Excel dosyasının adı.
    """
    if not products:
        print("Kaydedilecek ürün bulunamadı.")
        return

    try:
        # Adım 1: Kullanıcının ana dizinini bul (Örn: C:\Users\user)
        home_dir = Path.home()

        # Adım 2: İndirilenler klasörünün yolunu oluştur
        downloads_dir = home_dir / "Downloads"

        # Adım 3 (Güvenlik Önlemi): Eğer İndirilenler klasörü yoksa oluştur.
        # Bu, programın her durumda çalışmasını garanti eder.
        downloads_dir.mkdir(parents=True, exist_ok=True)

        # Adım 4: Dosyanın tam yolunu oluştur (Örn: C:\Users\user\Downloads\market_fiyatlari.xlsx)
        full_path = downloads_dir / filename

        # Ürün listesini bir pandas DataFrame'e çevir
        df = pd.DataFrame(products)

        # DataFrame'i hesaplanan tam yola kaydet
        df.to_excel(full_path, index=False)

        # Kullanıcıya dosyanın tam olarak nereye kaydedildiğini söyle
        print(f"✅ Veriler başarıyla '{full_path}' dosyasına kaydedildi.")

    except Exception as e:
        print(f"[HATA] Veriler Excel'e kaydedilirken bir sorun oluştu: {e}")
