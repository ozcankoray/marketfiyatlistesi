# src/core/mappings.py

# Bu dosya, config.py'deki alt kategorileri, sağladığınız
# TÜİK madde kodları listesiyle eşleştirir.

CATEGORY_TO_TUIK_CODE = {
    # Meyve ve Sebze
    "Meyve": "01161",  # Taze meyveler
    "Sebze": "01171",  # Taze sebzeler (patates hariç)

    # Et, Tavuk ve Balık
    "Kırmızı Et": "01122",  # Dana eti olarak temsil ediliyor
    "Beyaz Et": "01125",  # Tavuk eti olarak temsil ediliyor
    "Deniz Ürünleri": "01131",  # Taze balık
    "Şarküteri": "01127",  # Şarküteri ürünleri (sucuk, sosis, salam vb.)
    "Sakatat": "01126",  # Diğer etler ve yenilebilir sakatatlar

    # Süt Ürünleri ve Kahvaltılık
    "Süt": "01141",
    "Yumurta": "01145",
    "Peynir": "01144",
    "Yoğurt": "01143",  # Diğer süt ürünleri (yoğurt, hazır sütlü tatlı vb.)
    "Zeytin": "01190",  # Gri Alan: En yakın kategori "Başka yerde sınıflandırılamayan..." seçildi.
    "Tereyağı ve Margarin": "01151",  # Tereyağı olarak temsil ediliyor, margarin için 01152 de düşünülebilir.
    "Sürülebilir Ürünler ve Kahvaltılık Soslar": "01182",  # Gri Alan: En yakın kategori "Reçel, marmelat, bal vb."
    "Helva Tahin ve Pekmez": "01182",  # Gri Alan: En yakın kategori "Reçel, marmelat, bal vb."
    "Bal ve Reçel": "01182",
    "Kahvaltılık Gevrek Bar ve Granola": "01116",  # Kahvaltılık tahıl ürünleri
    "Kaymak ve Krema": "01143",  # Diğer süt ürünleri...

    # Temel Gıda
    "Ekmek ve Unlu Mamüller": "01113",  # Ekmek
    "Sıvı Yağlar": "01153",  # Sıvı yağlar (zeytinyağı, ayçiçek yağı)
    "Bakliyat": "01174",  # Kuru baklagiller
    "Şeker ve Tatlandırıcılar": "01181",  # Şeker
    "Pasta Malzemeleri": "01114",  # Diğer fırıncılık ürünleri...
    "Un ve İrmik": "01112",  # Un ve diğer tahıllar
    "Mantı Makarna ve Erişte": "01115",  # Makarna çeşitleri
    "Ketçap Mayonez Sos ve Sirkeler": "01190",  # Gri Alan: En yakın "Başka yerde..."
    "Tuz Baharat ve Harçlar": "01190",  # Gri Alan: En yakın "Başka yerde..."
    "Salça": "01175",  # Konserve edilmiş veya işlenmiş sebze içerikli
    "Turşu": "01175",  # Konserve edilmiş veya işlenmiş sebze içerikli
    "Konserve": "01175",
    "Hazır Gıda": "01190",  # Gri Alan: En yakın "Başka yerde..."
    "Bebek Mamaları": "01190",  # Gri Alan: En yakın "Başka yerde..."

    # İçecek
    "Su": "01221",  # Su ve maden suyu
    "Meyve Suyu": "01223",  # Meyve ve sebze suları
    "Gazlı İçecekler": "01222",  # Alkolsüz içecekler (meşrubat, ayran vb.)
    "Gazsız İçecekler": "01222",  # Alkolsüz içecekler (meşrubat, ayran vb.)
    "Ayran ve Kefir": "01222",  # Alkolsüz içecekler (meşrubat, ayran vb.)
    "Maden Suyu": "01221",  # Su ve maden suyu
    "Çay ve Bitki Çayları": "01212",
    "Kahve": "01211",

    # Atıştırmalık ve Tatlı
    "Çikolata": "01183",  # Çikolata ve şekerlemeler
    "Gofret": "01114",  # Diğer fırıncılık ürünleri (bisküvi, kek, kraker...)
    "Bisküvi ve Kraker": "01114",
    "Kek": "01114",
    "Cips": "01190",  # Gri Alan: En yakın "Başka yerde..."
    "Kuruyemiş ve Kuru Meyve": "01162",  # Kuru meyve ve sert kabuklu yemişler
    "Sakız ve Şekerleme": "01183",  # Çikolata ve şekerlemeler
    "Tatlılar": "01143",  # Diğer süt ürünleri (yoğurt, hazır sütlü tatlı vb.)
    "Dondurmalar": "01184",  # Dondurma

    # Temizlik ve Kişisel Bakım Ürünleri - BU GRUP GIDA DIŞI OLDUĞU İÇİN ŞİMDİLİK BOŞ BIRAKILABİLİR
    # Eğer bu grubu da dahil etmek isterseniz, ilgili kodları bulmanız gerekir.
}