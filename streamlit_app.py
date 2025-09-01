# streamlit_app.py

import streamlit as st
import pandas as pd
from datetime import datetime

# Importa le nostre funzioni dai moduli custom
import data_handler as dh
import financial_calculations as fc
import visualization as viz

st.set_page_config(layout="wide")

st.title("🔬 Laboratorio di Analisi Opzioni")
st.markdown("Inserisci i parametri di un'opzione per calcolare IV e Greche, e confrontarla con la volatilità storica del sottostante.")

# --- Sezione di Input nella Sidebar ---
with st.sidebar:
    st.header("Parametri dell'Opzione")
    
    ticker = st.text_input("Ticker Sottostante (es. ENI.MI)", "ENI.MI")
    option_type = st.selectbox("Tipo di Opzione", ["put", "call"])
    
    col1, col2 = st.columns(2)
    with col1:
        strike_price = st.number_input("Strike Price (K)", min_value=0.0, step=0.5, format="%.2f")
        premium = st.number_input("Premio (Prezzo Opzione)", min_value=0.0, step=0.01, format="%.3f")
    with col2:
        expiration_date = st.date_input("Data di Scadenza", value=datetime.now() + pd.Timedelta(days=30))
        risk_free_rate = st.slider("Tasso Risk-Free (r)", 0.0, 0.1, 0.04, format="%.3f")

    analyze_button = st.button("🚀 Analizza Opzione")

# --- Logica Principale e Visualizzazione ---
if analyze_button:
    if not all([ticker, strike_price, premium]):
        st.warning("Per favore, inserisci tutti i parametri richiesti.")
    else:
        with st.spinner(f"Recupero dati e calcolo in corso per {ticker}..."):
            # 1. Recupero Dati
            stock_data = dh.fetch_stock_data(ticker)
            
            if stock_data is None:
                st.error(f"Impossibile recuperare i dati per il ticker {ticker}. Controlla il simbolo.")
            else:
                current_stock_price = stock_data['Close'].iloc[-1]
                time_to_expiry = (expiration_date - datetime.now().date()).days / 365.0

                # 2. Calcoli Finanziari
                implied_vol = fc.calculate_implied_volatility(
                    target_price=premium,
                    S=current_stock_price,
                    K=strike_price,
                    T=time_to_expiry,
                    r=risk_free_rate,
                    option_type=option_type
                )
                
                if pd.isna(implied_vol):
                    st.error("Impossibile calcolare la Volatilità Implicita. Controlla che il premio sia coerente (es. non troppo basso/alto rispetto alla moneyness).")
                else:
                    greeks = fc.calculate_greeks(
                        S=current_stock_price,
                        K=strike_price,
                        T=time_to_expiry,
                        r=risk_free_rate,
                        sigma=implied_vol,
                        option_type=option_type
                    )
                    
                    hv_data = fc.calculate_historical_volatility(stock_data['Close'])

                    # 3. Visualizzazione dei Risultati
                    st.header(f"Risultati Analisi per {ticker}")
                    
                    # metriche chiave
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Prezzo Sottostante (S)", f"{current_stock_price:.2f}")
                    col2.metric("Volatilità Implicita (IV)", f"{implied_vol:.2%}")
                    col3.metric("Delta", f"{greeks['delta']:.3f}")
                    col4.metric("Theta (giornaliero)", f"{greeks['theta_per_day']:.4f}")
                    col5.metric("Vega (per 1% vol)", f"{greeks['vega']:.4f}")
                    
                    st.info(f"**Interpretazione:** Un Delta di **{greeks['delta']:.3f}** significa che per ogni €1 di aumento del sottostante, il prezzo dell'opzione cambierà di circa €{greeks['delta']:.3f}. Un Theta di **{greeks['theta_per_day']:.4f}** indica che l'opzione perde circa €{-greeks['theta_per_day']:.4f} di valore ogni giorno a causa del passare del tempo (time decay).", icon="🧠")
                    
                    st.markdown("---")
                    
                    # Grafico Volatility Cone
                    st.subheader("Confronto IV vs. Volatilità Storica (HV)")
                    cone_fig = viz.plot_volatility_cone(hv_data, implied_vol, ticker)
                    st.plotly_chart(cone_fig, use_container_width=True)
                    
                    st.info("**Interpretazione:** Il grafico mostra l'andamento della volatilità realizzata (storica) del sottostante su diverse finestre temporali. La linea rossa tratteggiata rappresenta la volatilità implicita che hai calcolato. Se la linea rossa si trova **al di sopra** delle linee della volatilità storica, specialmente nella parte alta del 'cono', il mercato sta prezzando un'incertezza futura maggiore rispetto a quella che si è manifestata storicamente. Questo può indicare un premio alla vendita potenzialmente 'caro'.", icon="💡")
