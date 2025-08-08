import time
from src.core import config
from src.core.database import init_db, insert_products_batch
from src.api.client import fetch_products_from_api
from src.parsers.product_parser import parse_products_data
from src.core.tuik_sepeti import TUIK_GIDA_SEPETI


def get_products_from_category(api_category_name: str) -> list:
    """
    Belirtilen tek bir API kategorisi için tüm sayfalardaki ham ürün verilerini çeker.
    """
    all_products_in_category = []
    current_page = 0

    while True:
        print(f"    -> '{api_category_name}' kategorisi için Sayfa {current_page + 1} taranıyor...")

        payload = config.get_category_payload(category_name=api_category_name, page=current_page)
        raw_data = fetch_products_from_api(config.CATEGORY_SEARCH_URL, config.HEADERS, payload)

        products_list = raw_data.get('content', []) if raw_data else []

        if products_list:
            all_products_in_category.extend(products_list)
            current_page += 1
            time.sleep(0.5)
        else:
            print(f"    -> '{api_category_name}' kategorisinde başka ürün bulunamadı.")
            break

    return all_products_in_category


def main():
    """Uygulamanın ana iş akışı."""
    start_time = time.time()
    print("🚀 Program Başlatılıyor...")

    init_db()

    print(f"\nAdım 2: TÜİK Gıda Sepeti taranıyor. Toplam {len(TUIK_GIDA_SEPETI)} madde işlenecek.")

    total_products_saved = 0
    processed_categories = set()

    for i, madde_item in enumerate(TUIK_GIDA_SEPETI, 1):
        madde_adi = madde_item['madde_adi']
        api_kategori_adi = madde_item.get("api_kategori_adi")

        print(f"\n({i}/{len(TUIK_GIDA_SEPETI)}) İşlenen Madde: '{madde_adi}' (Kategori: '{api_kategori_adi}')")

        if not api_kategori_adi:
            print(f"  ⚠️  '{madde_adi}' için 'api_kategori_adi' tanımlanmamış. Bu madde atlanıyor.")
            continue

        ham_urun_listesi = get_products_from_category(api_kategori_adi)

        if not ham_urun_listesi:
            print(f"  ⚠️  '{api_kategori_adi}' kategorisi için hiç ürün bulunamadı.")
            continue

        filtrelenmis_urunler = parse_products_data(ham_urun_listesi, madde_item)

        if filtrelenmis_urunler:
            insert_products_batch(filtrelenmis_urunler)
            count = len(filtrelenmis_urunler)
            total_products_saved += count
            print(f"  ✔️  '{madde_adi}' için {count} ürün filtrelendi ve veritabanına kaydedildi.")
        else:
            print(f"  ⚠️  '{madde_adi}' için filtrelenecek uygun ürün bulunamadı.")

    end_time = time.time()
    total_time = end_time - start_time

    print("\n" + "=" * 50)
    print("🎉 TÜM İŞLEMLER TAMAMLANDI 🎉")
    print(f"-> Toplam {total_products_saved} adet ürün verisi veritabanına aktarıldı.")
    print(f"-> Toplam süre: {total_time:.2f} saniye.")
    print("=" * 50)


if __name__ == "__main__":
    main()