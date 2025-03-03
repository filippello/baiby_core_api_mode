import re
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def decode_data(data: str):
    """
    Decodifica el data de la transacción para obtener el token identifier
    """
    try:
        if not data.startswith("composeTasks@"):
            return None, None
            
        parts = data.split("@")
        if len(parts) < 2:
            return None, None
            
        # Extraer el token identifier del data
        token_part = parts[1]
        token_hex = token_part[8:42] if len(token_part) >= 42 else None
        
        if not token_hex:
            return None, None
            
        # Convertir hex a string para obtener el token identifier
        try:
            token_bytes = bytes.fromhex(token_hex.replace('00', ''))
            token_identifier = token_bytes.decode('utf-8')
            return token_identifier, token_hex[24:48]  # Retorna token_id y amount_hex
        except:
            return None, None
            
    except Exception as e:
        logger.error(f"Error decoding data: {e}")
        return None, None

def get_token_id_from_identifier(token_identifier, platform="multiversx"):
    """
    Obtiene el token ID de CoinGecko usando el identificador del token
    """
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{platform}/contract/{token_identifier}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data["id"]
        else:
            logger.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error getting token ID: {e}")
        return None

def get_market_data(token_id, vs_currency="usd", days=30):
    """
    Obtiene datos de mercado de CoinGecko
    """
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "daily"
        }
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Error getting market data: {response.status_code}")
            
        return response.json()
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return None

def process_data(data):
    if not data or "prices" not in data:
        return None
    
    df = pd.DataFrame(data["prices"], columns=["date", "price"])
    df["returns"] = df["price"].pct_change()
    return df

def calculate_volatility(df):
    if df is None or df.empty:
        return None, None
        
    daily_vol = df["returns"].std()
    annual_vol = daily_vol * np.sqrt(365)
    return daily_vol, annual_vol

def assess_risk(volatility, amount=None):
    try:
        risk_level = "LOW"
        
        # Riesgo por volatilidad
        if volatility > 0.5:
            risk_level = "HIGH"
        elif volatility > 0.3:
            risk_level = "MEDIUM"
            
        # Ajustar por cantidad si está disponible
        if amount:
            amount_in_tokens = amount / 1e18
            if amount_in_tokens > 1000:
                risk_level = "HIGH"
            elif amount_in_tokens > 100 and risk_level != "HIGH":
                risk_level = "MEDIUM"
                
        return risk_level
    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        return "UNKNOWN"

def calculate_ash_risk(data: str):
    try:
        token_identifier, amount_hex = decode_data(data)
        if not token_identifier:
            return None
            
        # Obtener token ID de CoinGecko
        token_id = get_token_id_from_identifier(token_identifier)
        if not token_id:
            logger.warning(f"No se pudo obtener el token ID para {token_identifier}")
            return "UNKNOWN"
            
        # Obtener datos de mercado
        market_data = get_market_data(token_id)
        if not market_data:
            return "UNKNOWN"
            
        # Calcular volatilidad
        df = process_data(market_data)
        daily_vol, annual_vol = calculate_volatility(df)
        
        # Calcular amount si está disponible
        amount = int(amount_hex, 16) if amount_hex else None
        
        # Evaluar riesgo
        risk_level = assess_risk(annual_vol, amount)
        
        logger.info(f"Risk Analysis - Token: {token_identifier}, ID: {token_id}, Volatility: {annual_vol:.4f}, Risk: {risk_level}")
        return risk_level
        
    except Exception as e:
        logger.error(f"Error calculating risk: {e}")
        return None 