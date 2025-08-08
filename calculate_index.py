import sqlite3
import pandas as pd
from pathlib import Path
from datetime import date, timedelta, datetime
from scipy.stats import gmean
from collections import defaultdict

# --- Ayarlar ---
DB_FILE = Path(__file__).resolve().parent / "market_data.db"
BASE_INDEX_VALUE = 100.0


# --- Veritabanı ve Hesaplama Fonksiyonları (Değişiklik Yok) ---
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def get_available_dates() -> list:
    conn = get_db_connection()
    dates_df = pd.read_sql_query("SELECT DISTINCT cekilme_tarihi FROM Fiyatlar ORDER BY cekilme_tarihi", conn)
    conn.close()
    return [datetime.strptime(d, '%Y-%m-%d').date() for d in dates_df['cekilme_tarihi']]


def initialize_base_day(base_date: date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Endeksler WHERE tarih = ?", (str(base_date),))
    if cursor.fetchone()[0] > 0:
        print(f"Baz günü ({base_date}) zaten başlatılmış.")
        conn.close()
        return
    print(f"Baz günü ({base_date}) için endeks değerleri 100 olarak başlatılıyor...")
    cursor.execute("SELECT madde_kodu FROM Agirliklar")
    all_maddeler = cursor.fetchall()
    for madde in all_maddeler:
        cursor.execute(
            "INSERT OR IGNORE INTO Endeksler (madde_kodu, tarih, endeks_degeri) VALUES (?, ?, ?)",
            (str(madde['madde_kodu']), str(base_date), BASE_INDEX_VALUE)
        )
    conn.commit()
    conn.close()
    print("✅ Baz günü başlatma tamamlandı.")


def calculate_price_changes_hybrid(tarih_yeni: date, tarih_eski: date) -> pd.DataFrame:
    conn = get_db_connection()
    matched_query = """
                    WITH DunkuFiyatlar AS (SELECT tuik_madde_kodu, urun_adi, market, birim_fiyat \
                                           FROM Fiyatlar \
                                           WHERE cekilme_tarihi = ?),
                         BugunkuFiyatlar AS (SELECT tuik_madde_kodu, urun_adi, market, birim_fiyat \
                                             FROM Fiyatlar \
                                             WHERE cekilme_tarihi = ?)
                    SELECT d.tuik_madde_kodu, (b.birim_fiyat / d.birim_fiyat) AS fiyat_orani
                    FROM DunkuFiyatlar d \
                             JOIN BugunkuFiyatlar b ON d.urun_adi = b.urun_adi AND d.market = b.market
                    WHERE d.birim_fiyat > 0 \
                      AND b.birim_fiyat > 0 \
                    """
    matched_df = pd.read_sql_query(matched_query, conn, params=(str(tarih_eski), str(tarih_yeni)))

    matched_geo_means = pd.DataFrame()
    if not matched_df.empty:
        matched_geo_means = matched_df.groupby('tuik_madde_kodu')['fiyat_orani'].apply(gmean).reset_index()
        print(f"-> Model 1 (Eşleşme): {len(matched_geo_means)} madde için değişim hesaplandı.")

    avg_query = """
                WITH OrtalamaFiyatlar AS (SELECT cekilme_tarihi, tuik_madde_kodu, AVG(birim_fiyat) as ortalama_fiyat \
                                          FROM Fiyatlar \
                                          WHERE cekilme_tarihi IN (?, ?) \
                                            AND birim_fiyat IS NOT NULL \
                                          GROUP BY cekilme_tarihi, tuik_madde_kodu),
                     EskiOrtalama AS (SELECT tuik_madde_kodu, ortalama_fiyat \
                                      FROM OrtalamaFiyatlar \
                                      WHERE cekilme_tarihi = ?),
                     YeniOrtalama AS (SELECT tuik_madde_kodu, ortalama_fiyat \
                                      FROM OrtalamaFiyatlar \
                                      WHERE cekilme_tarihi = ?)
                SELECT e.tuik_madde_kodu, (y.ortalama_fiyat / e.ortalama_fiyat) AS fiyat_orani
                FROM EskiOrtalama e \
                         JOIN YeniOrtalama y ON e.tuik_madde_kodu = y.tuik_madde_kodu
                WHERE e.ortalama_fiyat > 0 \
                  AND y.ortalama_fiyat > 0 \
                """
    avg_df = pd.read_sql_query(avg_query, conn,
                               params=(str(tarih_eski), str(tarih_yeni), str(tarih_eski), str(tarih_yeni)))
    conn.close()

    final_changes = matched_geo_means.copy()
    if not avg_df.empty:
        fallback_df = avg_df[~avg_df['tuik_madde_kodu'].isin(final_changes['tuik_madde_kodu'])]
        if not fallback_df.empty:
            print(f"-> Model 2 (Ortalama): {len(fallback_df)} madde için fallback olarak değişim hesaplandı.")
            final_changes = pd.concat([final_changes, fallback_df], ignore_index=True)

    if final_changes.empty:
        return pd.DataFrame(columns=['tuik_madde_kodu', 'donemlik_degisim'])

    final_changes.rename(columns={'fiyat_orani': 'donemlik_degisim'}, inplace=True)
    final_changes['donemlik_degisim'] = final_changes['donemlik_degisim'] - 1

    return final_changes[['tuik_madde_kodu', 'donemlik_degisim']]


def update_index_for_date(tarih_yeni: date, tarih_eski: date):
    print(f"\n===== {tarih_yeni} İÇİN ENDEKS HESAPLAMA BAŞLADI (Baz: {tarih_eski}) =====")
    donemlik_degisimler = calculate_price_changes_hybrid(tarih_yeni, tarih_eski)
    conn = get_db_connection()
    eski_endeksler_df = pd.read_sql_query(
        "SELECT madde_kodu, endeks_degeri FROM Endeksler WHERE tarih = ?",
        conn, params=(str(tarih_eski),))
    eski_endeksler_df.rename(columns={'madde_kodu': 'tuik_madde_kodu'}, inplace=True)
    if eski_endeksler_df.empty:
        print(f"HATA: {tarih_eski} için endeks verisi bulunamadı!")
        conn.close()
        return
    merged_df = pd.merge(eski_endeksler_df, donemlik_degisimler, on='tuik_madde_kodu', how='left')
    merged_df['donemlik_degisim'] = merged_df['donemlik_degisim'].fillna(0)
    merged_df['yeni_endeks'] = merged_df['endeks_degeri'] * (1 + merged_df['donemlik_degisim'])
    cursor = conn.cursor()
    for _, row in merged_df.iterrows():
        cursor.execute(
            "INSERT OR REPLACE INTO Endeksler (madde_kodu, tarih, endeks_degeri) VALUES (?, ?, ?)",
            (row['tuik_madde_kodu'], str(tarih_yeni), row['yeni_endeks'])
        )
    conn.commit()
    conn.close()
    print(f"✅ {tarih_yeni} için {len(merged_df)} maddenin endeksi güncellendi.")


# --- YENİ EKLENEN FONKSİYON ---
def calculate_group_and_general_index(tarih: date) -> (float, dict):
    """
    Belirtilen bir tarih için hem Ana Grup bazında endeksleri hem de
    Genel Web-TÜFE endeksini hesaplar.
    """
    conn = get_db_connection()
    # Bu sefer tuik_sepeti'nden ana grup bilgisini de alıyoruz.
    query = """
            SELECT E.madde_kodu, \
                   E.endeks_degeri, \
                   A.agirlik
            FROM Endeksler E
                     JOIN Agirliklar A ON E.madde_kodu = A.madde_kodu
            WHERE E.tarih = ? \
            """
    df = pd.read_sql_query(query, conn, params=(str(tarih),))
    conn.close()

    if df.empty or df['agirlik'].sum() == 0:
        return 0.0, {}

    # tuik_sepeti'nden grup bilgilerini alıp DataFrame ile birleştir
    from src.core.tuik_sepeti import TUIK_GIDA_SEPETI
    grup_df = pd.DataFrame(TUIK_GIDA_SEPETI)[['madde_kodu', 'ana_grup_adi']]
    df = pd.merge(df, grup_df, on='madde_kodu', how='left')

    # Genel Endeksi Hesapla
    toplam_agirlikli_endeks = (df['endeks_degeri'] * df['agirlik']).sum()
    toplam_agirlik = df['agirlik'].sum()
    genel_endeks = toplam_agirlikli_endeks / toplam_agirlik

    # Grup Bazında Endeksleri Hesapla
    grup_endeksleri = {}
    for grup_adi, grup_df in df.groupby('ana_grup_adi'):
        grup_agirlikli_endeks = (grup_df['endeks_degeri'] * grup_df['agirlik']).sum()
        grup_toplam_agirlik = grup_df['agirlik'].sum()
        if grup_toplam_agirlik > 0:
            grup_endeksleri[grup_adi] = grup_agirlikli_endeks / grup_toplam_agirlik

    return genel_endeks, grup_endeksleri


# --- GÜNCELLENMİŞ ANA ÇALIŞTIRMA BLOĞU ---
if __name__ == "__main__":
    available_dates = get_available_dates()

    if not available_dates:
        print("Veritabanında hesaplama yapılacak hiç veri yok.")
    else:
        # Madde bazlı endeksleri hesapla
        base_date = available_dates[0]
        initialize_base_day(base_date)
        for i in range(1, len(available_dates)):
            update_index_for_date(available_dates[i], available_dates[i - 1])

        print("\n✅ Tüm mevcut tarihler için madde bazlı endeks hesaplaması tamamlandı!")

        # --- DETAYLI RAPORLAMA ---
        print("\n" + "=" * 60)
        print("📊 WEB-TÜFE (GIDA) DETAYLI ENDEKS VE ENFLASYON RAPORU 📊")
        print("=" * 60)

        # Her tarih için genel ve grup endekslerini topla
        rapor_verisi = {}
        for tarih in available_dates:
            genel_endeks, grup_endeksleri = calculate_group_and_general_index(tarih)
            rapor_verisi[tarih] = {"genel": genel_endeks, "gruplar": grup_endeksleri}

        # Son günün detaylı raporunu yazdır
        son_tarih = available_dates[-1]
        son_veri = rapor_verisi[son_tarih]
        print(f"--- {son_tarih} TARİHLİ GÜNCEL DURUM ---")
        print(f"Genel Gıda Endeksi: {son_veri['genel']:.2f}\n")
        print("Ana Grup Bazında Endeksler:")
        for grup, endeks in sorted(son_veri['gruplar'].items()):
            print(f"  - {grup:<25}: {endeks:.2f}")

        # Genel ve Grup bazında enflasyon oranlarını hesapla ve yazdır
        print("\n--- DÖNEMSEL ENFLASYON ANALİZİ ---")
        ilk_tarih = available_dates[0]
        ilk_veri = rapor_verisi[ilk_tarih]

        # Genel Enflasyon
        if ilk_veri['genel'] > 0:
            genel_enflasyon = ((son_veri['genel'] / ilk_veri['genel']) - 1) * 100
            print(f"Genel Gıda Enflasyonu ({ilk_tarih} -> {son_tarih}): % {genel_enflasyon:.2f}")

        # Grup Enflasyonları
        print("\nAna Grup Bazında Enflasyon Oranları:")
        for grup, ilk_grup_endeks in sorted(ilk_veri['gruplar'].items()):
            son_grup_endeks = son_veri['gruplar'].get(grup)
            if son_grup_endeks and ilk_grup_endeks > 0:
                grup_enflasyon = ((son_grup_endeks / ilk_grup_endeks) - 1) * 100
                print(f"  - {grup:<25}: % {grup_enflasyon:+.2f}")

        print("=" * 60)