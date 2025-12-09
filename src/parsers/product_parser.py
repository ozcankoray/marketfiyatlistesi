import re
from typing import List, Dict, Any, Tuple
from datetime import date
from src.utils.validators import validate_and_clean_products, check_duplicate_products


def extract_unit_and_quantity(name: str) -> Tuple[str, float]:
    """
    Ürün adından birim (gr, kg, ml, lt) ve miktar bilgilerini çıkarır.
    Adet, çarpım ve standart formatları daha akıllıca ele alır.
    """
    name_lower = name.lower().replace(',', '.')

    # --- ÖNCELİK 1: Çarpım formatı (örn: 6x200ml, 12*25 gr) ---
    # En spesifik olanı ilk arıyoruz.
    match = re.search(r'(\d+)\s*[x*]\s*(\d+\.?\d*)\s*(g|gr|ml|lt|l)', name_lower)
    if match:
        adet = float(match.group(1))
        miktar_tekil = float(match.group(2))
        birim_ham = match.group(3)
        toplam_miktar = adet * miktar_tekil

        if birim_ham in ['g', 'gr']: return 'gr', toplam_miktar
        if birim_ham in ['l', 'lt']: return 'ml', toplam_miktar * 1000
        if birim_ham == 'ml': return 'ml', toplam_miktar

    # --- ÖNCELİK 2: Standart ağırlık/hacim formatı (örn: 500 gr, 1.5 lt) ---
    match = re.search(r'(\d+\.?\d*)\s*(kg|gr|g|lt|l|ml)', name_lower)
    if match:
        miktar = float(match.group(1))
        birim = match.group(2)

        if birim == 'kg': return 'gr', miktar * 1000
        if birim in ['g', 'gr']: return 'gr', miktar
        if birim in ['lt', 'l']: return 'ml', miktar * 1000
        if birim == 'ml': return 'ml', miktar

    # --- ÖNCELİK 3: 'lu' veya 'li' ile biten adet formatı (örn: 100'lü, 15 li) ---
    # Bu, 'Lipton' gibi kelimelerdeki 'l' harfini litre olarak algılamamızı engeller.
    match = re.search(r"(\d+)\s*['\']?\s*(lu|li|lü)", name_lower)
    if match:
        miktar = float(match.group(1))
        return 'adet', miktar

    # --- Varsayılan Durum ---
    # Hiçbir format eşleşmezse, 1 adet olarak kabul et.
    return 'adet', 1.0


def parse_products_data(
        products_list: List[Dict[str, Any]],
        madde_item: dict
) -> List[Dict[str, Any]]:
    """
    Ham ürün listesini alır, filtreler, birim fiyatı hesaplar ve temiz bir liste döndürür.
    Geliştirilmiş versiyon: Veri validasyonu ve deduplication eklendi.
    
    Args:
        products_list: API'den gelen ham ürün listesi
        madde_item: TÜİK madde bilgisi (filtreleme kriterleri dahil)
    
    Returns:
        Temizlenmiş ve doğrulanmış ürün listesi
    """
    if not products_list:
        return []

    cleaned_products = []

    onay_listesi = madde_item.get("onay_kelimeleri", [])
    yasakli_liste = madde_item.get("yasakli_kelimeler", [])

    for product in products_list:
        if not isinstance(product, dict):
            continue

        urun_adi = product.get('title', 'İsim Bilgisi Yok')
        urun_adi_kucuk = urun_adi.lower()

        if yasakli_liste and any(kelime in urun_adi_kucuk for kelime in yasakli_liste):
            continue
        if onay_listesi and not any(kelime in urun_adi_kucuk for kelime in onay_listesi):
            continue

        orijinal_fiyat = 0.0
        market_name = 'Market Bilgisi Yok'
        veri_tarihi = date.today()

        depot_info_list = product.get('productDepotInfoList', [])
        if depot_info_list:
            first_depot_info = depot_info_list[0]
            if isinstance(first_depot_info, dict):
                orijinal_fiyat = first_depot_info.get('price', 0.0)
                market_name = first_depot_info.get('marketAdi', 'Market Bilgisi Yok')
                veri_tarihi_str = first_depot_info.get('indexTime', '').split(' ')[0]
                try:
                    veri_tarihi = date.fromisoformat(veri_tarihi_str)
                except (ValueError, TypeError):
                    veri_tarihi = date.today()

        # Birim ve miktar çıkarma
        birim, miktar = extract_unit_and_quantity(urun_adi)
        birim_fiyat = None

        # Birim fiyat hesaplama
        if miktar > 0 and orijinal_fiyat > 0:
            if birim == 'gr':  # kg fiyatı
                birim_fiyat = (orijinal_fiyat / miktar) * 1000
            elif birim == 'ml':  # litre fiyatı
                birim_fiyat = (orijinal_fiyat / miktar) * 1000

        cleaned_product = {
            'Ana Grup Adı': madde_item['ana_grup_adi'],
            'Madde Adı': madde_item['madde_adi'],
            'TÜİK Kodu': madde_item['madde_kodu'],
            'Ürün Adı': urun_adi,
            'Market': market_name.upper(),
            'Veri Tarihi': veri_tarihi,
            # Yeni eklenen alanlar
            'Orijinal Fiyat': orijinal_fiyat,
            'Birim': birim,
            'Miktar': miktar,
            'Birim Fiyat': birim_fiyat,
        }
        cleaned_products.append(cleaned_product)

    # Veri doğrulama ve deduplication
    cleaned_products = validate_and_clean_products(cleaned_products)
    cleaned_products = check_duplicate_products(cleaned_products)

    return cleaned_products