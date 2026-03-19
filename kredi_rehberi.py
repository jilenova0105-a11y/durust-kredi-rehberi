import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- CANLI VERİ ÇEKME FONKSİYONU (SCRAPING) ---
def piyasa_verilerini_kazila():
    url = "https://www.hangikredi.com/kredi/ihtiyac-kredisi"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        bankalar = {}
        # Sitedeki kredi tekliflerini buluyoruz
        kredi_kartlari = soup.find_all("div", class_="offer-list-item")
        for kart in kredi_kartlari:
            banka_adi = kart.get("data-bank-name")
            faiz_alani = kart.find("span", class_="interest-rate")
            if faiz_alani and banka_adi:
                faiz_metni = faiz_alani.text.replace("%", "").replace(",", ".").strip()
                bankalar[banka_adi] = float(faiz_metni)
        
        # Eğer veri çekilemezse boş kalmasın diye varsayılan değerler
        if not bankalar:
            return {"Garanti BBVA": 3.99, "Akbank": 4.15, "İş Bankası": 4.05}
        return bankalar
    except:
        return {"Garanti BBVA": 3.99, "Akbank": 4.15, "İş Bankası": 4.05}

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Dürüst Kredi Rehberi", layout="wide")
st.title("🛡️ Dürüst Kredi Analiz ve Karşılaştırma")
st.markdown("Bankaların gizlediği masrafları düşerek cebinize girecek **gerçek net parayı** hesaplar.")

# --- KULLANICI GİRİŞLERİ (YAN PANEL) ---
with st.sidebar:
    st.header("Kredi Ayarları")
    tutar = st.number_input("Talep Edilen Kredi (TL)", min_value=1000, value=100000, step=1000)
    vade = st.slider("Vade (Ay)", 3, 36, 12)
    st.divider()
    st.subheader("Ek Masraflar")
