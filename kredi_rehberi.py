import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- FONKSİYON: CANLI VERİ ÇEKME ---
def piyasa_verilerini_kazila(kredi_turu):
    # Kredi türüne göre URL belirleme (HangiKredi yapısına göre)
    turu_harita = {
        "İhtiyaç Kredisi": "ihtiyac-kredisi",
        "Konut Kredisi": "konut-kredisi",
        "0 KM Araç Kredisi": "tasit-kredisi",
        "2. El Araç Kredisi": "tasit-kredisi"
    }
    url = f"https://www.hangikredi.com/kredi/{turu_harita.get(kredi_turu, 'ihtiyac-kredisi')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        bankalar = {}
        kredi_kartlari = soup.find_all("div", class_="offer-list-item")
        for kart in kredi_kartlari:
            banka_adi = kart.get("data-bank-name")
            faiz_alani = kart.find("span", class_="interest-rate")
            if faiz_alani and banka_adi:
                faiz_metni = faiz_alani.text.replace("%", "").replace(",", ".").strip()
                bankalar[banka_adi] = float(faiz_metni)
        return bankalar if bankalar else {"Garanti BBVA": 3.99, "Akbank": 4.15, "İş Bankası": 4.05}
    except:
        return {"Garanti BBVA": 3.99, "Akbank": 4.15, "İş Bankası": 4.05}

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Dürüst Kredi Terminali", layout="wide")
st.title("🛡️ Profesyonel Kredi Analiz Terminali")

# --- SOL PANEL (GİRİŞLER) ---
with st.sidebar:
    st.header("📋 Kredi Parametreleri")
    
    # Kredi Türü Seçimi
    kredi_turu = st.selectbox("Kredi Türü Seçiniz", 
                              ["İhtiyaç Kredisi", "Konut Kredisi", "0 KM Araç Kredisi", "2. El Araç Kredisi"])
    
    # Tutar Girişi (Binlik ayraçlı formatlama Streamlit'te otomatik yapılır)
    tutar = st.number_input("Talep Edilen Kredi Tutarı (TL)", min_value=1000, value=100000, step=5000, format="%d")
    st.caption(f"Girilen Tutar: **{tutar:,} TL**".replace(",", ".")) # Kullanıcıya 100.000 formatında gösterir
    
    # Vade (120 Aya Kadar Elle Giriş)
    vade = st.number_input("Vade (Ay)", min_value=1, max_value=120, value=12, step=1)
    
    st.divider()
    st.subheader("🏦 Banka Kesinti Tahminleri")
    sigorta_tahmin = st.number_input("Hayat Sigortası (TL)", value=1500)
    ekspertiz_tahmin = st.number_input("Ekspertiz/Banka Ücreti (TL)", value=0)

# --- HESAPLAMA MOTORU ---
banka_oranlari = piyasa_verilerini_kazila(kredi_turu)
sonuclar = []

for banka, faiz in banka_oranlari.items():
    # Vergiler (KKDF %15 + BSMV %10 = %25) - Konut kredisinde vergiler 0'dır!
    vergi_orani = 1.25 if kredi_turu != "Konut Kredisi" else 1.00
    aylik_brut_faiz = (faiz * vergi_orani) / 100
    
    # Taksit Formülü
    taksit = tutar * (aylik_brut_faiz * (1 + aylik_brut_faiz)**vade) / ((1 + aylik_brut_faiz)**vade - 1)
    
    # Dinamik Masraf Hesaplama
    dosya_masrafi = tutar * 0.005 # Yasal sınır binde 5
    toplam_masraf = dosya_masrafi + sigorta_tahmin + ekspertiz_tahmin
    net_para = tutar - toplam_masraf
    toplam_odeme = taksit * vade
    
    sonuclar.append({
        "Banka": banka,
        "Faiz (%)": f"%{faiz}",
        "Net Nakit (Cebinize Giren)": f"{net_para:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."),
        "Aylık Taksit": f"{taksit:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."),
        "Dosya Masrafı": f"{dosya_masrafi:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."),
        "Toplam Geri Ödeme": f"{toplam_odeme:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
    })

# --- GÖRSELLEŞTİRME ---
st.subheader(f"📊 {kredi_turu} için {tutar:,} TL - {vade} Ay Vadeli Analiz")

# Dinamik Masraf Kartları (Hesaplama sonrası otomatik güncellenen alanlar)
c1, c2, c3 = st.columns(3)
c1.metric("Yasal Dosya Masrafı", f"{tutar * 0.005:,.0f} TL".replace(",", "."))
c2.metric("Tahmini Sigorta", f"{sigorta_tahmin:,.0f} TL".replace(",", "."))
c3.metric("Toplam Kesinti", f"{(tutar * 0.005) + sigorta_tahmin + ekspertiz_tahmin:,.0f} TL".replace(",", "."))

st.divider()
st.table(pd.DataFrame(sonuclar))

st.warning("ℹ️ **Önemli Bilgi:** Konut kredilerinde KKDF ve BSMV vergisi alınmadığı için hesaplamalar otomatik olarak vergisiz yapılmıştır.")
