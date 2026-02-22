import streamlit as st
import pandas as pd
import alpaca_trade_api as tradeapi
import os

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Alpha-5 Dashboard", layout="wide")

# Style CSS pour masquer les menus Streamlit et épurer l'interface
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background-color: #05070a;}
    </style>
    """, unsafe_allow_html=True)

# --- RÉCUPÉRATION DES SECRETS ---
try:
    # Utilisation des secrets Streamlit Cloud
    ALPACA_KEY = st.secrets["ALPACA_API_KEY"]
    ALPACA_SECRET = st.secrets["ALPACA_SECRET_KEY"]
    ALPACA_URL = st.secrets["ALPACA_BASE_URL"]
except Exception:
    # Fallback local pour tes tests personnels
    ALPACA_KEY = os.getenv("ALPACA_API_KEY")
    ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY")
    ALPACA_URL = os.getenv("ALPACA_BASE_URL")

# Connexion API
api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_URL, api_version='v2')

st.title("🚀 Alpha-5 : Terminal de Trading")

# --- SIMULATION DE TEST (MOCK DATA) ---
# Ce bloc permet de vérifier que tes alertes fonctionnent même le dimanche
class MockPosition:
    def __init__(self, symbol, profit_pc):
        self.symbol = symbol
        self.unrealized_intraday_plpc = profit_pc / 100
        self.qty = "10"
        self.current_price = "264.69"
        self.avg_entry_price = "252.08"

# On crée une liste de positions qui contient notre test
positions = [MockPosition("AAPL (TEST)", 4.65)]

# --- AFFICHAGE DES ALERTES DE PROFIT ---
st.subheader("Surveillance des Objectifs (+5%)")

for p in positions:
    profit = float(p.unrealized_intraday_plpc) * 100
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{p.symbol}** | Profit actuel : `{profit:.2f}%` / Objectif : `5.00%`")
        # Barre de progression (normée entre 0 et 1)
        progress_val = min(max(profit / 5.0, 0.0), 1.0)
        st.progress(progress_val)
    
    with col2:
        if profit >= 4.5:
            st.error(f"🔥 VENTE IMMINENTE")
        elif profit > 0:
            st.success(f"📈 En progression")

st.divider()

# --- DONNÉES RÉELLES DU COMPTE ---
try:
    account = api.get_account()
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Solde Cash", f"{float(account.cash):,.2f} $")
    col_b.metric("Valeur Portefeuille", f"{float
