# src/parsers/category_parser.py (Yeni Stratejiye Uygun)

from typing import Dict, List, Any, Optional

def parse_categories_to_map(raw_categories_content: Optional[List[Dict[str, Any]]]) -> Dict[str, List[str]]:
    """
    Ham kategori listesini, anahtarının ana kategori, değerinin alt kategori listesi
    olduğu bir sözlüğe (map) dönüştürür.

    Örnek Çıktı:
    {
        'Et, Tavuk ve Balık': ['Kırmızı Et', 'Beyaz Et', 'Deniz Ürünleri', ...],
        'Süt Ürünleri ve Kahvaltılık': ['Süt', 'Yumurta', 'Peynir', ...]
    }
    """
    if not raw_categories_content:
        return {}

    category_map = {}
    for main_category_data in raw_categories_content:
        if isinstance(main_category_data, dict):
            main_category_name = main_category_data.get('name')
            sub_categories = main_category_data.get('subcategories', [])
            if main_category_name and sub_categories:
                category_map[main_category_name] = sub_categories
    return category_map