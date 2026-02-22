import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpaca_trade_api.rest import REST
import os

# 1. CONFIGURATION INTERFACE (Doit toujours être la PREMIÈRE ligne Streamlit)
st.set_page_config(page_title="Alpha-5 Trading Dashboard", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Alpha-5 : Monitoring en Temps Réel")

# 2. CHARGEMENT SÉCURISÉ DES CLÉS
try:
    ALPACA_KEY = st.secrets["ALPACA_API_KEY"]
    ALPACA_SECRET = st.secrets["ALPACA_SECRET_KEY"]
    ALPACA_URL = st.secrets["ALPACA_BASE_URL"]
except Exception:
    # Si on teste en local sur ton PC (Fallback)
    ALPACA_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET = os.getenv('ALPACA_SECRET_KEY')
    ALPACA_URL = os.getenv('ALPACA_BASE_URL')

# 3. RÉCUPÉRATION DES DONNÉES
try:
    # Connexion Alpaca
    api = REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_URL)
    account = api.get_account()
    
    # --- SIMULATION DE TEST (MOCK DATA) POUR VOIR L'ALERTE ---
    class MockPosition:
        def __init__(self):
            self.symbol = "AAPL (TEST)"
            self.qty = "10"
            self.avg_entry_price = "252.08"
            self.current_price = "263.67"
            self.unrealized_intraday_plpc = 0.046 # 4.6% de profit
            self.market_value = "2636.70"

    positions = [MockPosition()] # On utilise notre fausse position pour le test

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
    df_positions = pd.DataFrame(pos_list)

    # --- BARRE DE MÉTRIQUES ---
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Solde Cash", f"{float(account.cash):.2f} $")
    col2.metric("📊 Valeur Portefeuille", f"{float(account.portfolio_value):.2f} $")
    profit_today = float(account.equity) - float(account.last_equity)
    col3.metric("📅 Profit Jour", f"{profit_today:.2f} $", f"{round((profit_today/float(account.last_equity))*100,2)}%")

    st.divider()

    # --- JAUGE DE PERFORMANCE ET ALERTE 🔥 ---
    st.subheader("🎯 Proximité de l'objectif (+5%)")
    if not df_positions.empty:
        for index, row in df_positions.iterrows():
            profit_pc = row['Profit/Perte %']
            progress = min(max(profit_pc / 5.0, 0.0), 1.0)
            
            st.write(f"**{row['Action']}** ({profit_pc}%)")
            st.progress(progress)
            
            if profit_pc >= 4.5:
                st.warning(f"🔥 {row['Action']} approche de l'objectif de vente !")

    st.divider()

    # --- TABLEAU DES OPÉRATIONS ---
    st.subheader("🔎 Opérations en cours")
    if not df_positions.empty:
        def color_profit(val):
            color = 'green' if val >= 4.5 else 'white'
            weight = 'bold' if val >= 4.5 else 'normal'
            return f'color: {color}; font-weight: {weight}'
        st.dataframe(df_positions.style.map(color_profit, subset=['Profit/Perte %']), use_container_width=True)
    else:
        st.info("Aucune position ouverte pour le moment. Le robot est en attente de signaux.")

except Exception as e:
    st.error(f"❌ Erreur de connexion au système : {e}")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write("🏦 **Compte lié :** Revolut Personnel")
st.sidebar.write("⏲️ **Prochain virement :** Vendredi 22h")
if st.sidebar.button("Rafraîchir les données"):
    st.rerun()
