import streamlit as st
import pandas as pd
from alpaca_trade_api.rest import REST
import os

# 1. IMPÉRATIF : st.set_page_config doit être la TOUTE PREMIÈRE ligne Streamlit
st.set_page_config(page_title="Alpha-5 Trading Dashboard", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Alpha-5 : Monitoring en Temps Réel")

# --- CONNEXION ALPACA SÉCURISÉE ---
try:
    # On gère correctement les secrets sur le Cloud ET en local
    try:
        API_KEY = st.secrets["ALPACA_API_KEY"]
        SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]
        BASE_URL = st.secrets["ALPACA_BASE_URL"]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        API_KEY = os.getenv('ALPACA_API_KEY')
        SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
        BASE_URL = os.getenv('ALPACA_BASE_URL')

    api = REST(API_KEY, SECRET_KEY, BASE_URL)
    account = api.get_account()

    # --- BARRE DE MÉTRIQUES ---
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Solde Cash", f"{float(
