import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpaca_trade_api.rest import REST
import os
from dotenv import load_dotenv

# --- CONFIGURATION INTERFACE ---
# Doit être la première commande Streamlit
st.set_page_config(page_title="Alpha-5 Trading Dashboard", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Alpha-5 : Monitoring en Temps Réel")

# Chargement des clés API
# Priorité aux Secrets Streamlit (Cloud), sinon .env (Local)
load_dotenv()

try:
    ALPACA_API_KEY = st.secrets["ALPACA_API_KEY"]
    ALPACA_SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]
    ALPACA_BASE_URL = st.secrets["ALPACA_BASE_URL"]
except Exception:
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL')

if not ALPACA_API_KEY:
    st.error("⚠️ Clés API manquantes ! Configurez les secrets sur Streamlit Cloud ou le fichier .env en local.")
    st.stop()

# Configuration Alpaca
try:
    api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
except Exception as e:
    st.error(f"Erreur d'initialisation Alpaca : {e}")
    st.stop()

# --- RÉCUPÉRATION DES DONNÉES ---
def get_data():
    account = api.get_account()
    positions = api.list_positions()

    # Transformation des positions en Tableau
    pos_list = []
    for p in positions:
        pos_list.append({
            "Action": p.symbol,
            "Quantité": p.qty,
            "Prix Achat": f"{float(p.avg_entry_price):.2f} $",
            "Prix Actuel": f"{float(p.current_price):.2f} $",
            "Profit/Perte %": round(float(p.unrealized_intraday_plpc) * 100, 2),
            "Valeur": f"{float(p.market_value):.2f} $"
        })
    return account, pd.DataFrame(pos_list), positions

try:
    account, df_positions, positions = get_data()

    # --- BARRE DE MÉTRIQUES ---
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Solde Cash", f"{float(account.cash):.2f} $")
    col2.metric("📊 Valeur Portefeuille", f"{float(account.portfolio_value):.2f} $")
    profit_today = float(account.equity) - float(account.last_equity)
    col3.metric("📅 Profit Jour", f"{profit_today:.2f} $", f"{round((profit_today/float(account.last_equity))*100,2)}%")

    st.divider()

    # --- TABLEAU DES OPÉRATIONS ---
    st.subheader("🔎 Opérations en cours")
    if not df_positions.empty:
        # On colore la colonne Profit pour voir tout de suite si on approche des +5%
        def color_profit(val):
            color = 'green' if val >= 4.5 else 'white'
            weight = 'bold' if val >= 4.5 else 'normal'
            return f'color: {color}; font-weight: {weight}'

        st.dataframe(df_positions.style.map(color_profit, subset=['Profit/Perte %']), use_container_width=True)
    else:
        st.info("Aucune position ouverte pour le moment. Le robot est en attente de signaux.")

    # --- JAUGE DE PERFORMANCE ---
    st.subheader("🎯 Proximité de l'objectif (+5%)")

    # --- TEST TEMPORAIRE AAPL (4.6%) ---
    class MockPosition:
        def __init__(self, symbol, plpc):
            self.symbol = symbol
            self.unrealized_intraday_plpc = plpc
    # On ajoute la position fictive pour vérifier l'affichage
    positions.append(MockPosition("AAPL (TEST)", 0.046))

    if positions:
        for p in positions:
            profit = float(p.unrealized_intraday_plpc) * 100
            st.write(f"**{p.symbol}** : {profit:.2f}% / 5.00%")
            st.progress(min(max(profit / 5.0, 0.0), 1.0))
            if profit >= 4.5:
                st.warning(f"🔥 {p.symbol} approche de l'objectif de vente !")

except Exception as e:
    st.error(f"Erreur de connexion aux APIs : {e}")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write("🏦 **Compte lié :** Revolut Personnel")
st.sidebar.write("⏲️ **Prochain virement :** Vendredi 22h")
if st.sidebar.button("Rafraîchir les données"):
    st.rerun()
