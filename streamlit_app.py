# streamlit_app.py (VERSIONE DEBUG)

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
    option_type = st.selectbox("Tipo di Opzione", ["put", "call"], index=1) # Default a 'call'
    
    col1, col2 = st.columns(2)
    with col1:
        strike_price = st.number_input("Strike Price (K)", min_value=0.0, step=0.5, value=9.8, format="%.2f")
        premium = st.number_input("Premio (Prezzo Opzione)", min_value=0.0, step=0.01, value=0.29, format="%.3f")
    with col2:
        # Default alla data specifica del tuo esempio
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
                
                # --- Sezione di Debug Aggiunta ---
                st.subheader("🕵️ Dati Intermedi per il Debug")
                debug_data = {
                    "Prezzo Sottostante (S)": current_stock_price,
                    "Strike Price (K)": strike_price,
                    "Premio (Target)": premium,
                    "Giorni alla Scadenza": (expiration_date - datetime.now().date()).days,
                    "Tempo alla Scadenza (T)": time_to_expiry,
                    "Tasso Risk-Free (r)": risk_free_rate,
                    "Tipo Opzione": option_type
                }
                st.json(debug_data)

                # Testiamo la funzione obiettivo ai limiti dell'intervallo di ricerca
                low_vol_price = fc.black_scholes_merton(current_stock_price, strike_price, time_to_expiry, risk_free_rate, 0.0001, option_type)
                high_vol_price = fc.black_scholes_merton(current_stock_price, strike_price, time_to_expiry, risk_free_rate, 5.0, option_type)
                
                st.write(f"**Valore BSM con Volatilità quasi zero (σ=0.01%):** `{low_vol_price:.4f}`")
                st.write(f"**Valore BSM con Volatilità altissima (σ=500%):** `{high_vol_price:.4f}`")
                st.write(f"**Funzione Obiettivo al limite inferiore (Prezzo BSM - Premio):** `{low_vol_price - premium:.4f}`")
                st.write(f"**Funzione Obiettivo al limite superiore (Prezzo BSM - Premio):** `{high_vol_price - premium:.4f}`")
                st.markdown("---")
                # --- Fine Sezione di Debug ---


                try:
                    implied_vol = fc.calculate_implied_volatility(
                        target_price=premium,
                        S=current_stock_price,
                        K=strike_price,
                        T=time_to_expiry,
                        r=risk_free_rate,
                        option_type=option_type
                    )
                    
                    if pd.isna(implied_vol):
                        st.error("Impossibile calcolare la Volatilità Implicita per un errore di convergenza numerica.")
                    else:
                        # ... resto del codice per visualizzare i risultati ...
                        st.success("Calcolo completato con successo!")
                        # (qui andrebbe il codice per mostrare metriche e grafici)

                except ValueError as e:
                    st.error(f"Errore durante il calcolo dell'IV: {e}")
