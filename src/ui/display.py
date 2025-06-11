# src/ui/display.py

"""
İşlenmiş veriyi kullanıcıya göstermekten sorumlu fonksiyonları içerir.
"""
from typing import List, Dict, Any

def display_products(products: List[Dict[str, Any]]):
    """
    Verilen ürün listesini formatlı bir şekilde konsola yazdırır.

    Args:
        products (List[Dict]): 'name', 'price', 'market' anahtarlarını içeren
                                 sözlüklerden oluşan liste.
    """
    if not products:
        print("\nBu kriterlere uygun gösterilecek ürün bulunamadı.")
        return

    print(f"\n--- Toplam {len(products)} Adet Ürün Bulundu ---\n")
    for product in products:
        print(f"🛒 Market: {product['market']}")
        print(f"  - Ürün: {product['name']}")
        print(f"  - Fiyat: {product['price']} TL")
        print("-" * 20)