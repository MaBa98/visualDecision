# financial_calculations.py

import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
from typing import Dict, List

# Costanti
TRADING_DAYS_PER_YEAR = 252

def black_scholes_merton(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """
    Calcola il prezzo di un'opzione Europea usando il modello di Black-Scholes-Merton.
    Versione BLINDATA per la massima stabilità numerica.
    """
    # 1. Gestione del tempo alla scadenza nullo o negativo
    if T <= 0:
        if option_type == "call":
            return max(0.0, S - K)
        elif option_type == "put":
            return max(0.0, K - S)
        else:
            raise ValueError("Il tipo di opzione deve essere 'call' o 'put'")

    # 2. Gestione della volatilità nulla o quasi nulla
    if sigma <= 1e-6:
        if option_type == "call":
            return max(0.0, S - K * np.exp(-r * T))
        else: # put
            return max(0.0, K * np.exp(-r * T) - S)
            
    # --- NUOVO CONTROLLO DI STABILITÀ NUMERICA ---
    # 3. Prevenzione della divisione per un numero infinitesimale
    denominator = sigma * np.sqrt(T)
    # Se il denominatore è troppo piccolo, la formula diventa instabile.
    # Il prezzo converge al suo valore intrinseco attualizzato.
    if denominator < 1e-8: # Un valore soglia molto piccolo
        if option_type == "call":
            return max(0.0, S - K * np.exp(-r * T))
        else: # put
            return max(0.0, K * np.exp(-r * T) - S)
    # --- FINE NUOVO CONTROLLO ---

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / denominator
    d2 = d1 - denominator
    
    if option_type == "call":
        price = (S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2))
    elif option_type == "put":
        price = (K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1))
    else:
        raise ValueError("Il tipo di opzione deve essere 'call' o 'put'")
        
    return price

def calculate_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> Dict[str, float]:
    """
    Calcola le Greche di primo ordine per un'opzione Europea.
    """
    if T == 0: T = 0.0001 # Evita divisione per zero alla scadenza
        
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    greeks = {}
    
    # Delta
    if option_type == "call":
        greeks["delta"] = norm.cdf(d1)
    else: # put
        greeks["delta"] = -norm.cdf(-d1)
        
    # Gamma
    greeks["gamma"] = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    # Vega (per 1% di cambio in vol)
    greeks["vega"] = 0.01 * (S * norm.pdf(d1) * np.sqrt(T))
    
    # Theta (annuale e giornaliero)
    if option_type == "call":
        theta_yearly = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
    else: # put
        theta_yearly = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
    greeks["theta_per_day"] = theta_yearly / 365
    
    return greeks

def calculate_implied_volatility(target_price: float, S: float, K: float, T: float, r: float, option_type: str) -> float:
    """
    Calcola la volatilità implicita usando il metodo di Brent.
    """
    # Funzione obiettivo: la differenza tra il prezzo di mercato e il prezzo BSM
    objective_function = lambda sigma: black_scholes_merton(S, K, T, r, sigma, option_type) - target_price
    
    try:
        # Brentq è un risolutore numerico robusto per trovare la radice (lo zero) della funzione
        iv = brentq(objective_function, a=1e-6, b=5.0) # Cerca IV tra 0.0001% e 500%
    except ValueError:
        iv = np.nan # Se non trova una soluzione
        
    return iv

def calculate_historical_volatility(price_data: pd.Series, windows: List[int] = [20, 30, 60, 90, 120]) -> pd.DataFrame:
    """
    Calcola la volatilità storica (realizzata) su diverse finestre temporali.
    """
    log_returns = np.log(price_data / price_data.shift(1))
    
    hv_data = pd.DataFrame(index=price_data.index)
    for w in windows:
        # Calcola la deviazione standard mobile dei log returns e annualizzala
        hv_data[f'HV_{w}d'] = log_returns.rolling(window=w).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
        
    return hv_data.dropna()
