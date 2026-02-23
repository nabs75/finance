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
    /* Supprimer les marges inutiles en haut */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    /* Style des blocs de stats ultra-compacts */
    [data-testid="stMetric"] {
        background-color: #0e1117 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        padding: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    /* Titre des stats (Cash, Valeur...) */
    [data-testid="stMetricLabel"] {
        font-size: 0.65rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #94a3b8 !important;
        margin-bottom: -10px !important;
    }
    /* Valeur numérique */
    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
        font-weight: 800 !important;
        color: #00d4ff !important;
    }
    /* Force l'alignement sur une seule ligne même sur mobile */
    [data-testid="stHorizontalBlock"] {
        gap: 8px !important;
    }
    /* Cacher le menu Streamlit pour gagner de la place */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

    cash_balance = float(account.cash)
    portfolio_value = float(account.portfolio_value)
    profit_today = float(account.equity) - float(account.last_equity)
    profit_pct = round((profit_today/float(account.last_equity))*100, 2)

    with col1:
        st.metric("Solde Cash", f"{cash_balance:,.2f} $")
    with col2:
        st.metric("Portefeuille", f"{portfolio_value:,.2f} $")
    with col3:
        # Affiche le profit du jour avec une flèche (delta)
        st.metric("Profit Jour", f"{profit_today:,.2f} $", delta=f"{profit_pct}%")

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
