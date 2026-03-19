import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- BANKA LOGOLARI SÖZLÜĞÜ ---
LOGOLAR = {
    "Garanti BBVA": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Garanti_BBVA_logo.svg/2560px-Garanti_BBVA_logo.svg.png",
    "Akbank": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Akbank_logo.svg/2560px-Akbank_logo.svg.png",
    "İş Bankası": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/T_Is_Bankasi_logo.svg/2560px-T_Is_Bankasi_logo.svg.png",
    "Ziraat Bankası": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Ziraat_Bankas%C4%B1_logo.svg/2560px-Ziraat_Bankas%C4%B1_logo.svg.png",
    "Yapı Kredi": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Yapi_Kredi_logo.svg/2560px-Yapi_Kredi_logo.svg.png",
    "QNB Finansbank": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/QNB_Finansbank_logo.svg/2560px-QNB_Finansbank_logo.svg.png",
    "TEB": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/TEB_Logo.svg/1200px-TEB_Logo.svg.png",
    "ING": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/ING_Group_N.V._Logo.svg/2560px-ING_Group_N.V._Logo.svg.png"
}

# --- FONKSİYON: CANLI VERİ ÇEKME ---
@st.cache_data(ttl=3600) # Verileri 1 saat hafızada tut (Hız için)
def piyasa_verilerini_kazila(kredi_turu):
    turu_harita = {"İhtiyaç Kredisi": "ihtiyac-kredisi", "Konut Kredisi": "konut-kredisi", "0 KM Araç Kredisi": "tasit-kredisi", "2. El Araç Kredisi": "tasit-kredisi"}
    url = f"https://www.hangikredi.com/kredi/{turu_harita.get(kredi_turu, 'ihtiyac-kredisi')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        bankalar = {}
        # Sitedeki tüm teklifleri (daha geniş bir liste için) tarıyoruz
        items = soup.find_all("div", class_="offer-list-item")
        for item in items:
            name = item.get("data-bank-name")
            rate_area = item.find("span", class_="interest-rate")
            if name and rate_area:
                rate = float(rate_area.text.replace("%", "").replace(",", ".").strip())
                bankalar[name] = rate
        return bankalar if len(bankalar) > 0 else {"Garanti BBVA": 3.99, "Akbank": 4.15, "İş Bankası": 4.05, "Ziraat Bankası": 3.80, "Yapı Kredi": 4.10}
    except:
        return {"Garanti BBVA": 3.99, "Akbank": 4.15, "İş Bankası": 4.05, "Ziraat Bankası": 3.80}

# --- ARAYÜZ ---
st.set_page_config(page_title="Dürüst Kredi Terminali", layout="wide")
st.title("🛡️ Profesyonel Kredi Analiz Terminali")

with st.sidebar:
    st.header("📋 Kredi Parametreleri")
    kredi_turu = st.selectbox("Kredi Türü", ["İhtiyaç Kredisi", "Konut Kredisi", "0 KM Araç Kredisi", "2. El Araç Kredisi"])
    tutar = st.number_input("Kredi Tutarı (TL)", min_value=1000, value=100000, step=5000)
    vade = st.number_input("Vade (Ay)", min_value=1, max_value=120, value=12)
    
    # HESAPLA BUTONU
    hesapla_btn = st.button("🚀 ŞİMDİ HESAPLA", use_container_width=True)
    
    st.divider()
    st.subheader("🏦 Masraflar")
    sigorta = st.number_input("Hayat Sigortası (TL)", value=1500)

if hesapla_btn:
    banka_oranlari = piyasa_verilerini_kazila(kredi_turu)
    
    st.subheader(f"📊 {kredi_turu} Analiz Sonuçları")
    
    # Her banka için bir satır oluştur (Logo + Detaylar)
    for banka, faiz in banka_oranlari.items():
        vergi = 1.25 if kredi_turu != "Konut Kredisi" else 1.00
        i = (faiz * vergi) / 100
        taksit = tutar * (i * (1 + i)**vade) / ((1 + i)**vade - 1)
        dosya = tutar * 0.005
        net_para = tutar - (dosya + sigorta)
        
        # Tasarım: Sol tarafta logo, sağ tarafta bilgiler
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
            
            with col1:
                logo_url = LOGOLAR.get(banka, "https://via.placeholder.com/100x50?text=BANKA")
                st.image(logo_url, width=100)
            
            with col2:
                st.write(f"**Banka:** {banka}")
                st.write(f"**Faiz:** %{faiz}")
            
            with col3:
                st.write(f"🛡️ **Net Nakit:** {net_para:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
                st.write(f"💳 **Aylık Taksit:** {taksit:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
            
            with col4:
                st.write(f"💰 **Toplam Ödeme:** {(taksit*vade):,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
                st.write(f"📄 **Dosya Masrafı:** {dosya:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))

else:
    st.info("👈 Lütfen sol taraftaki parametreleri ayarlayıp 'ŞİMDİ HESAPLA' butonuna basın.")
