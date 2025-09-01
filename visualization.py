# visualization.py

import pandas as pd
import plotly.graph_objects as go

def plot_volatility_cone(hv_data: pd.DataFrame, implied_volatility: float, ticker: str) -> go.Figure:
    """
    Crea un grafico del Volatility Cone e confronta con l'IV attuale.
    """
    fig = go.Figure()
    
    # Aggiungi le linee per ogni finestra di volatilità storica
    for col in hv_data.columns:
        fig.add_trace(go.Scatter(
            x=hv_data.index, 
            y=hv_data[col], 
            mode='lines',
            name=col
        ))
        
    # Aggiungi una linea orizzontale per la volatilità implicita calcolata
    fig.add_hline(
        y=implied_volatility, 
        line_dash="dash", 
        line_color="red", 
        annotation_text=f"IV Attuale: {implied_volatility:.2%}",
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        title=f"Volatility Cone per {ticker}",
        xaxis_title="Data",
        yaxis_title="Volatilità Annualizzata",
        yaxis_tickformat=".0%",
        legend_title="Finestre HV"
    )
    
    return fig
