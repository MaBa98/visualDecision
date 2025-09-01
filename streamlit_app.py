# streamlit_app.py (VERSIONE DEBUG - ORA FUNZIONANTE)

import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np

import data_handler as dh
import financial_calculations as fc
import visualization as viz

st.set_page_config(layout="wide")

st.title("🔬 Laboratorio di Analisi Opzioni")
st.markdown("Inserisci i parametri di un'opzione per calcolare IV e Greche, e confrontarla con la volatilità storica del sottostante.")

# --- Sezione di Input nella Sidebar ---
with st.sidebar:
    st.header("Parametri dell'Opzione")
    
    ticker = st.text_input("Ticker Sottostante (es. UEN.F)", "UEN.F")
    option_type = st.selectbox("Tipo di Opzione", ["put", "call"], index=1)
    
    col1, col2 = st.columns(2)
    with col1:
        strike_price = st.number_input("Strike Price (K)", min_value=0.0, step=0.5, value=9.8, format="%.2f")
        premium = st.number_input("Premio (Prezzo Opzione)", min_value=0.0, step=0.01, value=0.29, format="%.3f")
    with col2:
        expiration_date = st.date_input("Data di Scadenza", value=datetime(2025, 9, 19))
        risk_free_rate = st.slider("Tasso Risk-Free (r)", 0.0, 0.1, 0.04, format="%.3f")

    analyze_button = st.button("🚀 Analizza Opzione")

if analyze_button:
    if not all([ticker, strike_price, premium]):
        st.warning("Per favore, inserisci tutti i parametri richiesti.")
    else:
        with st.spinner(f"Recupero dati e calcolo in corso per {ticker}..."):
            stock_data = dh.fetch_stock_data(ticker)
            
            if stock_data is None:
                st.error(f"Impossibile recuperare i dati per il ticker {ticker}. Controlla il simbolo.")
            else:
                current_stock_price = stock_data['Close'].iloc[-1]
                time_to_expiry = (expiration_date - datetime.now().date()).days / 365.0
                
                # --- Sezione di Debug ---
                st.subheader("🕵️ Dati Intermedi per il Debug")
                debug_data = {
                    "Prezzo Sottostante (S)": current_stock_price,
                    "Strike Price (K)": strike_price,
                    "Premio (Target)": premium,
                    "Tempo alla Scadenza (T)": time_to_expiry,
                }
                st.json(debug_data)

                # Testiamo la funzione obiettivo ai limiti dell'intervallo di ricerca
                low_vol_price = fc.black_scholes_merton(current_stock_price, strike_price, time_to_expiry, risk_free_rate, 1e-6, option_type)
                high_vol_price = fc.black_scholes_merton(current_stock_price, strike_price, time_to_expiry, risk_free_rate, 5.0, option_type)
                
                st.write(f"**Prezzo BSM con Volatilità quasi zero:** `{low_vol_price:.4f}`")
                st.write(f"**Prezzo BSM con Volatilità altissima (500%):** `{high_vol_price:.4f}`")
                
                obj_func_low = low_vol_price - premium
                obj_func_high = high_vol_price - premium
                
                st.write(f"**Funzione Obiettivo al limite inferiore:** `{obj_func_low:.4f}`")
                st.write(f"**Funzione Obiettivo al limite superiore:** `{obj_func_high:.4f}`")
                
                st.markdown("---")
                
                # Esegui il calcolo principale
                # ... (il resto della logica va qui)
