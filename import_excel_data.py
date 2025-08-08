import pandas as pd
from pathlib import Path
from datetime import datetime

# Projemizdeki diğer modülleri import ediyoruz
from src.core.database import insert_products_batch, init_db
from src.parsers.product_parser import extract_unit_and_quantity
from src.core.tuik_sepeti import TUIK_GIDA_SEPETI

# --- KULLANICI AYARLARI ---
EXCEL_KLASOR_YOLU = r"C:\Users\user\Desktop\market fiyatları"  # Kendi yolunuzu yazın


def find_matching_madde(urun_adi: str):
    """
    Ürün adına bakarak, tuik_sepeti'nden en uygun maddeyi bulur.
    Daha spesifik (daha uzun) onay kelimeleri listesine sahip olan maddelere öncelik verir.
    """
    urun_adi_kucuk = urun_adi.lower()
    best_match = None
    max_specificity = -1

    for madde_item in TUIK_GIDA_SEPETI:
        onay_listesi = madde_item.get("onay_kelimeleri", [])
        yasakli_liste = madde_item.get("yasakli_kelimeler", [])

        # Önce yasaklı kelime var mı diye kontrol et, varsa bu maddeyi direkt geç
        if yasakli_liste and any(kelime in urun_adi_kucuk for kelime in yasakli_liste):
            continue

        # Onay kelimelerinden herhangi biri ürün adında geçiyor mu?
        if onay_listesi and any(kelime in urun_adi_kucuk for kelime in onay_listesi):
            # Eşleşme bulundu. Şimdi bu eşleşmenin ne kadar "spesifik" olduğuna bakalım.
            # Daha uzun bir onay listesi, daha spesifik bir eşleşme demektir.
            # Bu, "Peynir" ile "Beyaz Peynir" arasında doğru seçim yapmamıza yardımcı olur.
            specificity = len(" ".join(onay_listesi))
            if specificity > max_specificity:
                max_specificity = specificity
                best_match = madde_item

    return best_match


def process_and_import_excel(file_path: Path):
    """Tek bir Excel dosyasını okur, akıllıca işler ve veritabanına kaydeder."""
    print(f"\nİşleniyor: {file_path.name}")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"  [HATA] Dosya okunurken bir sorun oluştu: {e}")
        return

    try:
        tarih_str = file_path.stem.split('_')[-1]
        cekilme_tarihi = datetime.strptime(tarih_str, '%Y-%m-%d').date()
    except (IndexError, ValueError):
        print("  [HATA] Dosya adından tarih çıkarılamadı.")
        return

    products_to_insert = []
    unmatched_products = 0
    for index, row in df.iterrows():
        urun_adi = row.get('Ürün Adı')
        orijinal_fiyat = row.get('Fiyat')

        if not all([urun_adi, isinstance(orijinal_fiyat, (int, float))]):
            continue

        # Ürün adına göre en uygun TÜİK maddesini bul
        madde_item = find_matching_madde(urun_adi)
        if not madde_item:
            unmatched_products += 1
            continue

        birim, miktar = extract_unit_and_quantity(urun_adi)
        birim_fiyat = None
        if miktar > 0 and orijinal_fiyat > 0:
            if birim == 'gr':
                birim_fiyat = (orijinal_fiyat / miktar) * 1000
            elif birim == 'ml':
                birim_fiyat = (orijinal_fiyat / miktar) * 1000

        processed_product = {
            'Ana Grup Adı': madde_item['ana_grup_adi'],
            'Madde Adı': madde_item['madde_adi'],
            'TÜİK Kodu': madde_item['madde_kodu'],
            'Ürün Adı': urun_adi,
            'Market': row.get('Market'),
            'Veri Tarihi': cekilme_tarihi,
            'Orijinal Fiyat': orijinal_fiyat,
            'Birim': birim,
            'Miktar': miktar,
            'Birim Fiyat': birim_fiyat,
        }
        products_to_insert.append(processed_product)

    if products_to_insert:
        insert_products_batch(products_to_insert)
        print(f"  ✅ {len(products_to_insert)} ürün veritabanına aktarıldı.")
    if unmatched_products > 0:
        print(f"  ⚠️ {unmatched_products} ürün için eşleşen bir madde bulunamadı ve atlandı.")


def import_all_excels_from_folder(folder_path: str):
    """Belirtilen klasördeki tüm uygun Excel dosyalarını işler."""
    path = Path(folder_path)
    if not path.is_dir():
        print(f"[HATA] Klasör bulunamadı: {folder_path}")
        return

    init_db()
    excel_files = sorted(list(path.glob("market_fiyatlari_*.xlsx")))
    print(f"Toplam {len(excel_files)} adet Excel dosyası bulundu. İçe aktarma başlıyor...")

    for file in excel_files:
        process_and_import_excel(file)

    print("\n🎉 Tüm Excel dosyalarının içe aktarımı tamamlandı! 🎉")


if __name__ == "__main__":
    import_all_excels_from_folder(EXCEL_KLASOR_YOLU)