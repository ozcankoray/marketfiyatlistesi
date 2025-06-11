# src/exporters/to_excel.py

"""
İşlenmiş veriyi Excel dosyasına aktarmaktan sorumlu fonksiyonları içerir.
"""
import pandas as pd
from typing import List, Dict, Any

def save_to_excel(products: List[Dict[str, Any]], filename: str = "market_fiyatlari.xlsx"):
    """
    Verilen ürün listesini bir pandas DataFrame'e dönüştürür ve Excel dosyasına kaydeder.

    Args:
        products (List[Dict]): Kaydedilecek ürünlerin listesi.
        filename (str): Oluşturulacak Excel dosyasının adı.
    """
    if not products:
        print("Kaydedilecek ürün bulunamadı.")
        return

    try:
        # Ürün listesini bir pandas DataFrame'e çevir
        df = pd.DataFrame(products)

        # DataFrame'i bir Excel dosyasına kaydet
        # index=False, Excel'e gereksiz bir sütun (0, 1, 2...) eklenmesini önler.
        df.to_excel(filename, index=False)
        print(f"✅ Veriler başarıyla '{filename}' dosyasına kaydedildi.")

    except Exception as e:
        print(f"[HATA] Veriler Excel'e kaydedilirken bir sorun oluştu: {e}")