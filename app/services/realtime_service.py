"""Real-time data service for stocks, weather, and time"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
import aiohttp
import pytz

logger = logging.getLogger(__name__)


class RealtimeService:
    """Service for fetching real-time data from external APIs"""

    def __init__(self):
        """Initialize realtime service"""
        # Free API endpoints (no key required for basic usage)
        self.stock_api = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.weather_api = "https://wttr.in"
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time stock price using Yahoo Finance

        Args:
            symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)

        Returns:
            Dictionary with stock data
        """
        try:
            symbol = symbol.upper().strip()
            url = f"{self.stock_api}/{symbol}?interval=1d&range=1d"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("chart", {}).get("result", [])
                        
                        if result:
                            meta = result[0].get("meta", {})
                            price = meta.get("regularMarketPrice", 0)
                            prev_close = meta.get("previousClose", 0)
                            currency = meta.get("currency", "USD")
                            name = meta.get("shortName", symbol)
                            
                            # Calculate change
                            change = price - prev_close
                            change_percent = (change / prev_close * 100) if prev_close else 0
                            
                            return {
                                "success": True,
                                "symbol": symbol,
                                "name": name,
                                "price": round(price, 2),
                                "change": round(change, 2),
                                "change_percent": round(change_percent, 2),
                                "currency": currency,
                            }
                        
            return {"success": False, "error": f"Stock symbol '{symbol}' not found"}
            
        except Exception as e:
            logger.error(f"Error fetching stock price: {e}")
            return {"success": False, "error": str(e)}

    async def get_weather(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city using wttr.in (free, no API key)

        Args:
            city: City name

        Returns:
            Dictionary with weather data
        """
        try:
            city = city.strip().replace(" ", "+")
            url = f"{self.weather_api}/{city}?format=j1"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        current = data.get("current_condition", [{}])[0]
                        location = data.get("nearest_area", [{}])[0]
                        
                        city_name = location.get("areaName", [{}])[0].get("value", city)
                        country = location.get("country", [{}])[0].get("value", "")
                        
                        temp_c = current.get("temp_C", "N/A")
                        temp_f = current.get("temp_F", "N/A")
                        feels_like_c = current.get("FeelsLikeC", "N/A")
                        humidity = current.get("humidity", "N/A")
                        description = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
                        wind_kmph = current.get("windspeedKmph", "N/A")
                        
                        return {
                            "success": True,
                            "city": city_name,
                            "country": country,
                            "temperature_c": temp_c,
                            "temperature_f": temp_f,
                            "feels_like_c": feels_like_c,
                            "humidity": humidity,
                            "description": description,
                            "wind_kmph": wind_kmph,
                        }
            
            return {"success": False, "error": f"Weather data not found for '{city}'"}
            
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return {"success": False, "error": str(e)}

    def get_time_in_city(self, city: str) -> Dict[str, Any]:
        """
        Get current time in a city/timezone

        Args:
            city: City name or timezone

        Returns:
            Dictionary with time data
        """
        try:
            city_lower = city.lower().strip()
            
            # Common city to timezone mapping
            city_timezones = {
                # Americas
                "new york": "America/New_York",
                "nyc": "America/New_York",
                "los angeles": "America/Los_Angeles",
                "la": "America/Los_Angeles",
                "chicago": "America/Chicago",
                "san francisco": "America/Los_Angeles",
                "seattle": "America/Los_Angeles",
                "miami": "America/New_York",
                "toronto": "America/Toronto",
                "vancouver": "America/Vancouver",
                "mexico city": "America/Mexico_City",
                "sao paulo": "America/Sao_Paulo",
                
                # Europe
                "london": "Europe/London",
                "paris": "Europe/Paris",
                "berlin": "Europe/Berlin",
                "madrid": "Europe/Madrid",
                "rome": "Europe/Rome",
                "amsterdam": "Europe/Amsterdam",
                "moscow": "Europe/Moscow",
                "zurich": "Europe/Zurich",
                
                # Asia
                "tokyo": "Asia/Tokyo",
                "osaka": "Asia/Tokyo",
                "beijing": "Asia/Shanghai",
                "shanghai": "Asia/Shanghai",
                "hong kong": "Asia/Hong_Kong",
                "singapore": "Asia/Singapore",
                "seoul": "Asia/Seoul",
                "bangkok": "Asia/Bangkok",
                "dubai": "Asia/Dubai",
                "mumbai": "Asia/Kolkata",
                "delhi": "Asia/Kolkata",
                "bangalore": "Asia/Kolkata",
                "bengaluru": "Asia/Kolkata",
                "chennai": "Asia/Kolkata",
                "kolkata": "Asia/Kolkata",
                "hyderabad": "Asia/Kolkata",
                "karachi": "Asia/Karachi",
                "jakarta": "Asia/Jakarta",
                "manila": "Asia/Manila",
                "taipei": "Asia/Taipei",
                "kuala lumpur": "Asia/Kuala_Lumpur",
                
                # Australia/Pacific
                "sydney": "Australia/Sydney",
                "melbourne": "Australia/Melbourne",
                "auckland": "Pacific/Auckland",
                "perth": "Australia/Perth",
                
                # Africa/Middle East
                "cairo": "Africa/Cairo",
                "johannesburg": "Africa/Johannesburg",
                "nairobi": "Africa/Nairobi",
                "tel aviv": "Asia/Jerusalem",
                "riyadh": "Asia/Riyadh",
            }
            
            # Find timezone
            tz_name = city_timezones.get(city_lower)
            
            if not tz_name:
                # Try to find partial match
                for key, value in city_timezones.items():
                    if city_lower in key or key in city_lower:
                        tz_name = value
                        break
            
            if not tz_name:
                # Try direct timezone name
                try:
                    tz = pytz.timezone(city)
                    tz_name = city
                except:
                    return {
                        "success": False,
                        "error": f"Unknown city/timezone: '{city}'. Try major cities like Tokyo, London, New York."
                    }
            
            # Get current time in that timezone
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            
            return {
                "success": True,
                "city": city.title(),
                "timezone": tz_name,
                "time": now.strftime("%I:%M %p"),  # 12-hour format
                "time_24": now.strftime("%H:%M"),  # 24-hour format
                "date": now.strftime("%A, %B %d, %Y"),
                "full": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            }
            
        except Exception as e:
            logger.error(f"Error getting time: {e}")
            return {"success": False, "error": str(e)}

    async def get_crypto_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get cryptocurrency price

        Args:
            symbol: Crypto symbol (BTC, ETH, etc.)

        Returns:
            Dictionary with crypto data
        """
        try:
            symbol = symbol.upper().strip()
            
            # Map common names to symbols
            crypto_map = {
                "BITCOIN": "BTC",
                "ETHEREUM": "ETH",
                "DOGECOIN": "DOGE",
                "RIPPLE": "XRP",
                "CARDANO": "ADA",
                "SOLANA": "SOL",
            }
            symbol = crypto_map.get(symbol, symbol)
            
            # Use CoinGecko free API
            coin_ids = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "DOGE": "dogecoin",
                "XRP": "ripple",
                "ADA": "cardano",
                "SOL": "solana",
                "DOT": "polkadot",
                "MATIC": "matic-network",
                "LTC": "litecoin",
            }
            
            coin_id = coin_ids.get(symbol, symbol.lower())
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if coin_id in data:
                            price = data[coin_id].get("usd", 0)
                            change_24h = data[coin_id].get("usd_24h_change", 0)
                            
                            return {
                                "success": True,
                                "symbol": symbol,
                                "name": coin_id.title(),
                                "price": round(price, 2),
                                "change_24h": round(change_24h, 2),
                                "currency": "USD",
                            }
            
            return {"success": False, "error": f"Cryptocurrency '{symbol}' not found"}
            
        except Exception as e:
            logger.error(f"Error fetching crypto price: {e}")
            return {"success": False, "error": str(e)}
