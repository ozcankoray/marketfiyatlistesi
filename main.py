# main.py (En Güncel ve Tam Sürüm - Zaman Damgalı Kayıt)

import sys
import time
from datetime import datetime
from src.core import config
from src.api.client import fetch_products_from_api
from src.parsers.product_parser import parse_products_data
from src.exporters.to_excel import save_to_excel


def get_all_products_from_subcategory(main_category: str, sub_category: str) -> list:
    """
    Bir alt kategoriye ait TÜM sayfalardaki ürünleri, API'den boş bir ürün listesi
    gelene kadar çeker. Bu en güvenilir yöntemdir.
    """
    all_products_in_subcategory = []
    current_page = 0

    while True:
        print(f"    -> Sayfa {current_page + 1} taranıyor...")
        payload = config.get_payload(sub_category, page=current_page, is_menu_category=False)

        raw_data_response = fetch_products_from_api(
            url=config.SEARCH_API_URL,
            headers=config.HEADERS,
            payload=payload
        )

        if not raw_data_response:
            print("    -> API'den yanıt alınamadı, bu kategori atlanıyor.")
            break

        # API'den gelen ham ürün listesini kontrol et
        products_list = raw_data_response.get('content', [])

        if products_list:  # Eğer bu liste boş DEĞİLSE, ürün var demektir.
            parsed_products = parse_products_data(products_list, main_category, sub_category)
            all_products_in_subcategory.extend(parsed_products)
            current_page += 1  # Bir sonraki sayfaya geç
            time.sleep(0.5)
        else:  # Eğer bu liste BOŞ İSE, bu kategorideki tüm sayfalar bitti demektir.
            print("    -> Bu kategoride başka ürün bulunamadı. Tarama tamamlandı.")
            break  # Döngüyü sonlandır.

    return all_products_in_subcategory


def main():
    """Uygulamanın ana iş akışı."""
    print("🚀 Program Başlatılıyor...")

    # Adım 1: Kategori Yapısını Oku
    print("\nAdım 1: Kategori yapısı doğrudan konfigürasyon dosyasından okunuyor...")
    category_structure = config.CATEGORY_STRUCTURE
    total_sub_categories = sum(len(sub_cats) for sub_cats in category_structure.values())
    print(
        f"✅ Başarılı! {len(category_structure)} ana kategori ve {total_sub_categories} alt kategori işlenmek üzere yüklendi.")

    # Adım 2: Her Alt Kategori İçin Doğrudan Arama
    all_products_total = []
    print("\nAdım 2: Her bir alt kategori için ürünler taranıyor...")

    for main_cat, sub_cats_list in category_structure.items():
        for sub_cat in sub_cats_list:
            print(f"\n Kategori: '{main_cat}' -> Alt Kategori: '{sub_cat}'")
            products_from_subcategory = get_all_products_from_subcategory(main_cat, sub_cat)

            if products_from_subcategory:
                print(
                    f"  ✔️  '{sub_cat}' alt kategorisinden toplam {len(products_from_subcategory)} adet ürün çekildi.")
                all_products_total.extend(products_from_subcategory)
            else:
                print(f"  ⚠️  '{sub_cat}' alt kategorisi için hiç ürün bulunamadı.")

    # Adım 3: Dinamik Dosya Adı Oluşturma ve Excel'e Kaydetme

    # Bugünün tarihini "YYYY-AA-GG" formatında al
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Dosya adını bu tarih damgasıyla birleştir
    filename = f"market_fiyatlari_{today_str}.xlsx"

    print(f"\nAdım 3: Toplamda bulunan {len(all_products_total)} adet ürün Excel'e kaydediliyor...")
    print(f"  -> Dosya adı: {filename}")

    save_to_excel(all_products_total, filename=filename)

    print(f"\n✅ Tüm işlemler tamamlandı. {len(all_products_total)} ürün '{filename}' dosyasına yazıldı.")


if __name__ == "__main__":
    main()
