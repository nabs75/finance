import streamlit as st
import pandas as pd
import alpaca_trade_api as tradeapi
import os

# --- RÉCUPÉRATION DES SECRETS STREAMLIT ---
# Sur Streamlit Cloud, on utilise st.secrets au lieu de os.getenv
try:
    ALPACA_KEY = st.secrets["ALPACA_API_KEY"]
    ALPACA_SECRET = st.secrets["ALPACA_SECRET_KEY"]
    ALPACA_URL = st.secrets["ALPACA_BASE_URL"]
except KeyError:
    st.error("❌ Erreur : Les clés API ne sont pas configurées dans les Secrets de Streamlit.")
    st.stop()

# Connexion à l'API
api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_URL, api_version='v2')

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Alpha-5 Dashboard", layout="wide")

st.title("🚀 Alpha-5 : Terminal de Trading")

def get_account_info():
    try:
        account = api.get_account()
        positions = api.list_positions()
        return account, positions
    except Exception as e:
        st.error(f"❌ Erreur de connexion Alpaca : {e}")
        return None, None

account, positions = get_account_info()

if account:
    # Affichage des métriques
    col1, col2 = st.columns(2)
    col1.metric("Solde Cash", f"{float(account.cash):.2f} $")
    col2.metric("Valeur Portefeuille", f"{float(account.portfolio_value):.2f} $")

    # Affichage des positions
    st.subheader("Positions Actuelles")
    if positions:
        df = pd.DataFrame([p._raw for p in positions])
        st.dataframe(df)
    else:
        st.write("Aucune position ouverte. Le bot est en attente.")
