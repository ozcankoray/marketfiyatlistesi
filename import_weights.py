import sqlite3
from pathlib import Path
from collections import defaultdict
from src.core.agirlik_sinif_2024 import SINIF_AGIRLIKLARI_2024
from src.core.agirlik_madde_2022 import MADDE_AGIRLIKLARI_2022
from src.core.tuik_sepeti import TUIK_GIDA_SEPETI

DB_FILE = Path(__file__).resolve().parent / "market_data.db"


def calculate_and_import_weights():
    print("Oransal dağıtım ile madde ağırlıkları tahmin ediliyor...")

    # 1. Her sınıfın 2022'deki toplam ağırlığını hesapla
    sinif_toplam_agirlik_2022 = defaultdict(float)
    for madde_kodu, agirlik in MADDE_AGIRLIKLARI_2022.items():
        sinif_kodu = madde_kodu[:5]
        sinif_toplam_agirlik_2022[sinif_kodu] += agirlik

    # 2. Her maddenin tahmini 2024 ağırlığını hesapla
    tahmini_agirliklar_2024 = []
    for madde in TUIK_GIDA_SEPETI:
        madde_kodu = madde['madde_kodu']
        sinif_kodu = madde_kodu[:5]

        agirlik_2022 = MADDE_AGIRLIKLARI_2022.get(madde_kodu, 0)
        toplam_sinif_2022 = sinif_toplam_agirlik_2022.get(sinif_kodu, 0)
        toplam_sinif_2024 = SINIF_AGIRLIKLARI_2024.get(sinif_kodu, 0)

        tahmini_agirlik = 0.0
        if agirlik_2022 > 0 and toplam_sinif_2022 > 0 and toplam_sinif_2024 > 0:
            # Maddenin 2022'deki oransal payını bul
            oransal_pay = agirlik_2022 / toplam_sinif_2022
            # Bu payı, sınıfın 2024'teki yeni toplam ağırlığıyla çarp
            tahmini_agirlik = oransal_pay * toplam_sinif_2024

        tahmini_agirliklar_2024.append({
            "madde_kodu": madde_kodu,
            "madde_adi": madde['madde_adi'],
            "agirlik": tahmini_agirlik
        })

    # 3. Hesaplanan ağırlıkları veritabanına yaz
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS Agirliklar;")
    cursor.execute("""
                   CREATE TABLE Agirliklar
                   (
                       madde_kodu TEXT PRIMARY KEY,
                       madde_adi  TEXT,
                       agirlik    REAL NOT NULL
                   );
                   """)
    for item in tahmini_agirliklar_2024:
        cursor.execute(
            "INSERT INTO Agirliklar (madde_kodu, madde_adi, agirlik) VALUES (?, ?, ?)",
            (item['madde_kodu'], item['madde_adi'], item['agirlik'])
        )
    conn.commit()
    conn.close()

    print(f"✅ {len(tahmini_agirliklar_2024)} adet tahmini 2024 madde ağırlığı 'Agirliklar' tablosuna aktarıldı.")


if __name__ == "__main__":
    calculate_and_import_weights()