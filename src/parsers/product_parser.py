# src/parsers/product_parser.py (En Basit ve Doğru Hali)

from typing import List, Dict, Any, Optional

def parse_products_data(
    products_list: Optional[List[Dict[str, Any]]],
    main_category: str,
    sub_category: str # Artık bu bilginin %100 doğru olduğunu biliyoruz
) -> List[Dict[str, Any]]:
    """
    Ham ürün listesini alır ve verilen kategori bilgileriyle birleştirerek temiz bir liste döndürür.
    """
    if not products_list:
        return []

    cleaned_products = []
    for product in products_list:
        if not isinstance(product, dict):
            continue

        product_price = 0.0
        market_name = 'Market Bilgisi Yok'
        depot_info_list = product.get('productDepotInfoList', [])
        if depot_info_list:
            first_depot_info = depot_info_list[0]
            if isinstance(first_depot_info, dict):
                product_price = first_depot_info.get('price', 0.0)
                market_name = first_depot_info.get('marketAdi', 'Market Bilgisi Yok')

        cleaned_product = {
            'Ana Kategori': main_category,
            'Alt Kategori': sub_category, # Doğrudan gelen parametreyi yaz
            'Ürün Adı': product.get('title', 'İsim Bilgisi Yok'),
            'Fiyat': product_price,
            'Market': market_name.upper()
        }
        cleaned_products.append(cleaned_product)

    return cleaned_products