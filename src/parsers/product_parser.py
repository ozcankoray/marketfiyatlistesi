# src/parsers/product_parser.py (Tarih Sütunu Eklendi)

from typing import List, Dict, Any, Optional


def parse_products_data(
        products_list: Optional[List[Dict[str, Any]]],
        main_category: str,
        sub_category: str
) -> List[Dict[str, Any]]:
    """
    Ham ürün listesini alır ve tarih bilgisiyle zenginleştirerek temiz bir liste döndürür.
    """
    if not products_list:
        return []

    cleaned_products = []
    for product in products_list:
        if not isinstance(product, dict):
            continue

        product_price = 0.0
        market_name = 'Market Bilgisi Yok'
        index_time = 'Tarih Bilgisi Yok'

        depot_info_list = product.get('productDepotInfoList', [])
        if depot_info_list:
            first_depot_info = depot_info_list[0]
            if isinstance(first_depot_info, dict):
                product_price = first_depot_info.get('price', 0.0)
                market_name = first_depot_info.get('marketAdi', 'Market Bilgisi Yok')
                # indexTime'ı da buradan alıyoruz ve sadece tarih kısmını alıyoruz (boşluktan bölerek)
                index_time = first_depot_info.get('indexTime', 'Tarih Bilgisi Yok').split(' ')[0]

        cleaned_product = {
            'Ana Kategori': main_category,
            'Alt Kategori': sub_category,
            'Ürün Adı': product.get('title', 'İsim Bilgisi Yok'),
            'Fiyat': product_price,
            'Market': market_name.upper(),
            'Veri Tarihi': index_time  # Yeni sütunumuz
        }
        cleaned_products.append(cleaned_product)

    return cleaned_products
