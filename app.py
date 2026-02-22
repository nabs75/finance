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

# --- SIMULATION VISUELLE (TEST DU WEEK-END) ---
# On force l'affichage de l'alerte pour que tu puisses valider le design
st.subheader("🎯 Test de la jauge (+5%)")
mock_profit = 4.65
st.write(f"**AAPL (TEST)** ({mock_profit}%)")
st.progress(min(max(mock_profit / 5.0, 0.0), 1.0))
if mock_profit >= 4.5:
    st.warning("🔥 AAPL (TEST) approche de l'objectif de vente !")
st.divider()

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
    col1.metric("💰 Solde Cash", f"{float(account.cash):.2f} $")
    col2.metric("📊 Valeur Portefeuille", f"{float(account.portfolio_value):.2f} $")
    profit_today = float(account.equity) - float(account.last_equity)
    col3.metric("📅 Profit Jour", f"{profit_today:.2f} $")

    st.divider()

    # --- TABLEAU DES OPÉRATIONS RÉELLES ---
    st.subheader("🔎 Opérations en cours")
    positions = api.list_positions()

    if positions:
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
        df_positions = pd.DataFrame(pos_list)

        def color_profit(val):
            color = '#00ff88' if val >= 4.5 else 'white'
            weight = 'bold' if val >= 4.5 else 'normal'
            return f'color: {color}; font-weight: {weight}'

        st.dataframe(df_positions.style.map(color_profit, subset=['Profit/Perte %']), use_container_width=True)
        
        # Jauges réelles
        for index, row in df_positions.iterrows():
            progress = min(max(row['Profit/Perte %'] / 5.0, 0.0), 1.0)
            if row['Profit/Perte %'] >= 4.5:
                st.warning(f"🔥 {row['Action']} approche de l'objectif de vente !")

    else:
        st.info("Aucune position ouverte pour le moment. Le robot est en attente de signaux.")

except Exception as e:
    st.error(f"❌ Erreur de connexion aux APIs : {e}")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write("🏦 **Compte lié :** Revolut Personnel")
st.sidebar.write("⏲️ **Prochain virement :** Vendredi 22h")
if st.sidebar.button("Rafraîchir les données"):
    st.rerun()
