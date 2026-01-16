"""
General Purpose Tools - Comprehensive set of tools for common use cases
Compatible with Qwen3-4B-toolcalling model trained on xlam-function-calling-60k dataset
"""

from .base import BaseTool
from datetime import datetime, timedelta
import json
import math
import random


# ============================================================================
# WEATHER & CLIMATE TOOLS
# ============================================================================

class GetWeatherTool(BaseTool):
    """Get current weather information for any location"""
    
    @property
    def name(self):
        return "get_weather"
    
    @property
    def description(self):
        return "Fetches current weather information including temperature, humidity, and conditions for a specified location."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, address, or coordinates (e.g., 'New York', 'London, UK', '40.7128,-74.0060')"
                },
                "units": {
                    "type": "string",
                    "description": "Temperature unit: 'celsius', 'fahrenheit', or 'kelvin'",
                    "enum": ["celsius", "fahrenheit", "kelvin"]
                }
            },
            "required": ["location"]
        }
    
    def execute(self, location: str, units: str = "celsius") -> dict:
        # Simulated weather data
        temp_base = random.randint(15, 30)
        if units == "fahrenheit":
            temp = temp_base * 9/5 + 32
        elif units == "kelvin":
            temp = temp_base + 273.15
        else:
            temp = temp_base
        
        conditions = ["sunny", "cloudy", "partly cloudy", "rainy", "windy"]
        
        return {
            "location": location,
            "temperature": round(temp, 1),
            "units": units,
            "condition": random.choice(conditions),
            "humidity": random.randint(40, 80),
            "wind_speed": random.randint(5, 25),
            "timestamp": datetime.now().isoformat()
        }


class GetForecastTool(BaseTool):
    """Get weather forecast for multiple days"""
    
    @property
    def name(self):
        return "get_forecast"
    
    @property
    def description(self):
        return "Retrieves weather forecast for a specified location for the next N days."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or coordinates"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to forecast (1-14)",
                    "minimum": 1,
                    "maximum": 14
                },
                "units": {
                    "type": "string",
                    "description": "Temperature unit",
                    "enum": ["celsius", "fahrenheit", "kelvin"]
                }
            },
            "required": ["location", "days"]
        }
    
    def execute(self, location: str, days: int, units: str = "celsius") -> dict:
        forecast = []
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            temp_base = random.randint(15, 30)
            
            if units == "fahrenheit":
                temp = temp_base * 9/5 + 32
            elif units == "kelvin":
                temp = temp_base + 273.15
            else:
                temp = temp_base
            
            forecast.append({
                "date": date,
                "temperature": round(temp, 1),
                "condition": random.choice(["sunny", "cloudy", "rainy"]),
                "precipitation_chance": random.randint(0, 100)
            })
        
        return {
            "location": location,
            "units": units,
            "forecast": forecast
        }


# ============================================================================
# FINANCIAL TOOLS
# ============================================================================

class CurrencyConverterTool(BaseTool):
    """Convert between different currencies"""
    
    @property
    def name(self):
        return "convert_currency"
    
    @property
    def description(self):
        return "Converts an amount from one currency to another using current exchange rates."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "Amount to convert"
                },
                "from_currency": {
                    "type": "string",
                    "description": "Source currency code (e.g., 'USD', 'EUR', 'GBP')"
                },
                "to_currency": {
                    "type": "string",
                    "description": "Target currency code"
                }
            },
            "required": ["amount", "from_currency", "to_currency"]
        }
    
    def execute(self, amount: float, from_currency: str, to_currency: str) -> dict:
        # Simulated exchange rates
        rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.0,
            "BRL": 5.0,
            "CAD": 1.25,
            "AUD": 1.35,
            "CNY": 6.45
        }
        
        from_rate = rates.get(from_currency.upper(), 1.0)
        to_rate = rates.get(to_currency.upper(), 1.0)
        
        # Convert to USD first, then to target currency
        usd_amount = amount / from_rate
        converted_amount = usd_amount * to_rate
        
        return {
            "original_amount": amount,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "converted_amount": round(converted_amount, 2),
            "exchange_rate": round(to_rate / from_rate, 4),
            "timestamp": datetime.now().isoformat()
        }


class StockPriceTool(BaseTool):
    """Get current stock price and information"""
    
    @property
    def name(self):
        return "get_stock_price"
    
    @property
    def description(self):
        return "Retrieves current stock price, change, and basic information for a given stock ticker."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'TSLA')"
                },
                "include_details": {
                    "type": "boolean",
                    "description": "Include additional details like volume, market cap, etc."
                }
            },
            "required": ["ticker"]
        }
    
    def execute(self, ticker: str, include_details: bool = False) -> dict:
        base_price = random.uniform(50, 500)
        change = random.uniform(-5, 5)
        
        result = {
            "ticker": ticker.upper(),
            "price": round(base_price, 2),
            "change": round(change, 2),
            "change_percent": round((change / base_price) * 100, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        if include_details:
            result.update({
                "volume": random.randint(1000000, 50000000),
                "market_cap": f"${random.randint(10, 1000)}B",
                "52_week_high": round(base_price * 1.2, 2),
                "52_week_low": round(base_price * 0.8, 2)
            })
        
        return result


# ============================================================================
# MATHEMATICAL TOOLS
# ============================================================================

class AdvancedCalculatorTool(BaseTool):
    """Advanced mathematical calculations"""
    
    @property
    def name(self):
        return "advanced_calculator"
    
    @property
    def description(self):
        return """Performs advanced mathematical operations. 
Examples: 
- Square 25: {"operation": "power", "values": [25, 2]}
- Square root of 16: {"operation": "sqrt", "values": [16]}
- Factorial of 5: {"operation": "factorial", "values": [5]}"""
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Mathematical operation to perform",
                    "enum": ["factorial", "power", "sqrt", "log", "sin", "cos", "tan", "mean", "median", "std_dev"]
                },
                "values": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Array of numbers. For power: [base, exponent]. For sqrt/factorial: [number]. For stats: [number1, number2, ...]"
                }
            },
            "required": ["operation", "values"]
        }
    
    def execute(self, operation: str, values: list) -> dict:
        try:
            if operation == "factorial":
                result = math.factorial(int(values[0]))
            elif operation == "power":
                result = math.pow(values[0], values[1])
            elif operation == "sqrt":
                result = math.sqrt(values[0])
            elif operation == "log":
                result = math.log(values[0], values[1] if len(values) > 1 else math.e)
            elif operation == "sin":
                result = math.sin(math.radians(values[0]))
            elif operation == "cos":
                result = math.cos(math.radians(values[0]))
            elif operation == "tan":
                result = math.tan(math.radians(values[0]))
            elif operation == "mean":
                result = sum(values) / len(values)
            elif operation == "median":
                sorted_vals = sorted(values)
                n = len(sorted_vals)
                result = sorted_vals[n//2] if n % 2 else (sorted_vals[n//2-1] + sorted_vals[n//2]) / 2
            elif operation == "std_dev":
                mean = sum(values) / len(values)
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                result = math.sqrt(variance)
            else:
                return {"error": f"Unknown operation: {operation}"}
            
            return {
                "operation": operation,
                "input": values,
                "result": round(result, 6) if isinstance(result, float) else result
            }
        except Exception as e:
            return {"error": str(e)}


# ============================================================================
# TEXT PROCESSING TOOLS
# ============================================================================

class TextAnalysisTool(BaseTool):
    """Analyze text for various metrics"""
    
    @property
    def name(self):
        return "analyze_text"
    
    @property
    def description(self):
        return "Analyzes text to extract metrics like word count, character count, sentiment, and readability."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to analyze"
                },
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["word_count", "char_count", "sentence_count", "avg_word_length", "sentiment"]
                    },
                    "description": "Metrics to calculate"
                }
            },
            "required": ["text"]
        }
    
    def execute(self, text: str, metrics: list = None) -> dict:
        if metrics is None:
            metrics = ["word_count", "char_count", "sentence_count"]
        
        words = text.split()
        sentences = text.split('.')
        
        result = {}
        
        if "word_count" in metrics:
            result["word_count"] = len(words)
        
        if "char_count" in metrics:
            result["char_count"] = len(text)
            result["char_count_no_spaces"] = len(text.replace(" ", ""))
        
        if "sentence_count" in metrics:
            result["sentence_count"] = len([s for s in sentences if s.strip()])
        
        if "avg_word_length" in metrics:
            result["avg_word_length"] = round(sum(len(w) for w in words) / len(words), 2) if words else 0
        
        if "sentiment" in metrics:
            # Simplified sentiment analysis
            positive_words = ["good", "great", "excellent", "happy", "love", "amazing"]
            negative_words = ["bad", "terrible", "hate", "sad", "awful", "poor"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            result["sentiment"] = sentiment
            result["sentiment_score"] = {
                "positive": positive_count,
                "negative": negative_count
            }
        
        return result


class TranslateTool(BaseTool):
    """Translate text between languages"""
    
    @property
    def name(self):
        return "translate_text"
    
    @property
    def description(self):
        return "Translates text from one language to another."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to translate"
                },
                "source_language": {
                    "type": "string",
                    "description": "Source language code (e.g., 'en', 'es', 'fr', 'de')"
                },
                "target_language": {
                    "type": "string",
                    "description": "Target language code"
                }
            },
            "required": ["text", "target_language"]
        }
    
    def execute(self, text: str, target_language: str, source_language: str = "auto") -> dict:
        # Simulated translation
        translations = {
            "en": {"hello": "hello", "world": "world"},
            "es": {"hello": "hola", "world": "mundo"},
            "fr": {"hello": "bonjour", "world": "monde"},
            "de": {"hello": "hallo", "world": "welt"},
            "pt": {"hello": "olá", "world": "mundo"}
        }
        
        return {
            "original_text": text,
            "translated_text": f"[Translated to {target_language}]: {text}",
            "source_language": source_language,
            "target_language": target_language,
            "confidence": 0.95
        }


# ============================================================================
# DATE & TIME TOOLS
# ============================================================================

class DateTimeTool(BaseTool):
    """Work with dates and times"""
    
    @property
    def name(self):
        return "datetime_operations"
    
    @property
    def description(self):
        return "Performs various date and time operations including conversions, calculations, and formatting."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Date/time operation to perform",
                    "enum": [
                        "current_time", "get_current_year", "get_current_month", "get_current_day",
                        "add_days", "subtract_days", "format_date", "time_difference", "timezone_convert"
                    ]
                },
                "date": {
                    "type": "string",
                    "description": "Date in ISO format (YYYY-MM-DD)"
                },
                "value": {
                    "type": "integer",
                    "description": "Numeric value for calculations"
                },
                "format": {
                    "type": "string",
                    "description": "Output format pattern"
                },
                "timezone": {
                    "type": "string",
                    "description": "Timezone name (e.g., 'UTC', 'America/New_York')"
                }
            },
            "required": ["operation"]
        }
    
    def execute(self, operation: str, date: str = None, value: int = None, 
                format: str = None, timezone: str = None) -> dict:
        try:
            if operation == "current_time":
                now = datetime.now()
                return {
                    "datetime": now.isoformat(),
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S"),
                    "timestamp": int(now.timestamp())
                }
            
            elif operation == "get_current_year":
                now = datetime.now()
                return {
                    "year": now.year,
                    "full_date": now.strftime("%Y-%m-%d")
                }
            
            elif operation == "get_current_month":
                now = datetime.now()
                return {
                    "month": now.month,
                    "month_name": now.strftime("%B"),
                    "month_abbr": now.strftime("%b"),
                    "full_date": now.strftime("%Y-%m-%d")
                }
            
            elif operation == "get_current_day":
                now = datetime.now()
                return {
                    "day": now.day,
                    "day_of_week": now.strftime("%A"),
                    "day_of_week_abbr": now.strftime("%a"),
                    "full_date": now.strftime("%Y-%m-%d")
                }
            
            elif operation == "add_days":
                base_date = datetime.fromisoformat(date) if date else datetime.now()
                new_date = base_date + timedelta(days=value)
                return {
                    "original_date": base_date.strftime("%Y-%m-%d"),
                    "days_added": value,
                    "result_date": new_date.strftime("%Y-%m-%d")
                }
            
            elif operation == "subtract_days":
                base_date = datetime.fromisoformat(date) if date else datetime.now()
                new_date = base_date - timedelta(days=value)
                return {
                    "original_date": base_date.strftime("%Y-%m-%d"),
                    "days_subtracted": value,
                    "result_date": new_date.strftime("%Y-%m-%d")
                }
            
            elif operation == "format_date":
                base_date = datetime.fromisoformat(date) if date else datetime.now()
                formats = {
                    "short": "%Y-%m-%d",
                    "long": "%A, %B %d, %Y",
                    "iso": "%Y-%m-%dT%H:%M:%S",
                    "us": "%m/%d/%Y"
                }
                fmt = formats.get(format, "%Y-%m-%d")
                return {
                    "date": base_date.strftime(fmt)
                }
            
            elif operation == "time_difference":
                # Requires two dates
                return {
                    "error": "time_difference requires two dates to compare"
                }
            
            else:
                return {"error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return {"error": str(e)}


# ============================================================================
# WEB & SEARCH TOOLS
# ============================================================================

class WebSearchTool(BaseTool):
    """Search the web for information"""
    
    @property
    def name(self):
        return "web_search"
    
    @property
    def description(self):
        return "Searches the web for information on a given query and returns relevant results."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (1-20)",
                    "minimum": 1,
                    "maximum": 20
                },
                "language": {
                    "type": "string",
                    "description": "Language for results (e.g., 'en', 'es', 'fr')"
                }
            },
            "required": ["query"]
        }
    
    def execute(self, query: str, num_results: int = 10, language: str = "en") -> dict:
        # Simulated search results
        results = []
        for i in range(min(num_results, 5)):
            results.append({
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is a relevant snippet about {query}...",
                "position": i + 1
            })
        
        return {
            "query": query,
            "num_results": len(results),
            "language": language,
            "results": results
        }


class URLFetchTool(BaseTool):
    """Fetch content from a URL"""
    
    @property
    def name(self):
        return "fetch_url"
    
    @property
    def description(self):
        return "Fetches content from a specified URL and extracts text, metadata, or specific elements."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to fetch"
                },
                "extract": {
                    "type": "string",
                    "description": "What to extract from the page",
                    "enum": ["text", "title", "links", "images", "metadata", "all"]
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds"
                }
            },
            "required": ["url"]
        }
    
    def execute(self, url: str, extract: str = "text", timeout: int = 30) -> dict:
        # Simulated URL fetch
        return {
            "url": url,
            "status_code": 200,
            "title": "Example Page Title",
            "text": "This is the extracted text content from the page...",
            "links": ["https://example.com/link1", "https://example.com/link2"],
            "images": ["https://example.com/image1.jpg"],
            "metadata": {
                "description": "Page description",
                "keywords": ["example", "test"]
            }
        }


# ============================================================================
# LOCATION & GEOGRAPHY TOOLS
# ============================================================================

class GeocodeTool(BaseTool):
    """Convert addresses to coordinates and vice versa"""
    
    @property
    def name(self):
        return "geocode"
    
    @property
    def description(self):
        return "Converts an address to geographic coordinates (latitude/longitude) or vice versa."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Address to geocode"
                },
                "latitude": {
                    "type": "number",
                    "description": "Latitude for reverse geocoding"
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude for reverse geocoding"
                },
                "reverse": {
                    "type": "boolean",
                    "description": "If true, convert coordinates to address"
                }
            }
        }
    
    def execute(self, address: str = None, latitude: float = None, 
                longitude: float = None, reverse: bool = False) -> dict:
        if reverse and latitude and longitude:
            # Reverse geocoding
            return {
                "latitude": latitude,
                "longitude": longitude,
                "address": f"123 Example St, City, Country",
                "place_name": "Example Place",
                "postal_code": "12345"
            }
        elif address:
            # Forward geocoding
            lat = random.uniform(-90, 90)
            lon = random.uniform(-180, 180)
            return {
                "address": address,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "confidence": 0.95
            }
        else:
            return {"error": "Either address or coordinates required"}


class DistanceCalculatorTool(BaseTool):
    """Calculate distance between two locations"""
    
    @property
    def name(self):
        return "calculate_distance"
    
    @property
    def description(self):
        return "Calculates the distance between two geographic points using their coordinates."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "origin_lat": {
                    "type": "number",
                    "description": "Latitude of origin point"
                },
                "origin_lon": {
                    "type": "number",
                    "description": "Longitude of origin point"
                },
                "dest_lat": {
                    "type": "number",
                    "description": "Latitude of destination point"
                },
                "dest_lon": {
                    "type": "number",
                    "description": "Longitude of destination point"
                },
                "unit": {
                    "type": "string",
                    "description": "Unit of measurement",
                    "enum": ["km", "miles", "meters"]
                }
            },
            "required": ["origin_lat", "origin_lon", "dest_lat", "dest_lon"]
        }
    
    def execute(self, origin_lat: float, origin_lon: float, 
                dest_lat: float, dest_lon: float, unit: str = "km") -> dict:
        # Haversine formula
        R = 6371  # Earth radius in km
        
        lat1, lon1 = math.radians(origin_lat), math.radians(origin_lon)
        lat2, lon2 = math.radians(dest_lat), math.radians(dest_lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        distance_km = R * c
        
        if unit == "miles":
            distance = distance_km * 0.621371
        elif unit == "meters":
            distance = distance_km * 1000
        else:
            distance = distance_km
        
        return {
            "origin": {"latitude": origin_lat, "longitude": origin_lon},
            "destination": {"latitude": dest_lat, "longitude": dest_lon},
            "distance": round(distance, 2),
            "unit": unit
        }


# ============================================================================
# DATA PROCESSING TOOLS
# ============================================================================

class JSONProcessorTool(BaseTool):
    """Process and manipulate JSON data"""
    
    @property
    def name(self):
        return "process_json"
    
    @property
    def description(self):
        return "Processes JSON data with operations like validation, extraction, transformation, and formatting."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "json_data": {
                    "type": "string",
                    "description": "JSON string to process"
                },
                "operation": {
                    "type": "string",
                    "description": "Operation to perform",
                    "enum": ["validate", "pretty_print", "minify", "extract_keys", "get_value"]
                },
                "path": {
                    "type": "string",
                    "description": "JSON path for extraction (e.g., 'user.name')"
                }
            },
            "required": ["json_data", "operation"]
        }
    
    def execute(self, json_data: str, operation: str, path: str = None) -> dict:
        try:
            data = json.loads(json_data)
            
            if operation == "validate":
                return {
                    "valid": True,
                    "message": "JSON is valid"
                }
            
            elif operation == "pretty_print":
                return {
                    "formatted": json.dumps(data, indent=2)
                }
            
            elif operation == "minify":
                return {
                    "minified": json.dumps(data, separators=(',', ':'))
                }
            
            elif operation == "extract_keys":
                keys = list(data.keys()) if isinstance(data, dict) else []
                return {
                    "keys": keys,
                    "count": len(keys)
                }
            
            elif operation == "get_value":
                if not path:
                    return {"error": "Path required for get_value operation"}
                
                keys = path.split('.')
                value = data
                for key in keys:
                    value = value.get(key) if isinstance(value, dict) else None
                
                return {
                    "path": path,
                    "value": value
                }
            
            else:
                return {"error": f"Unknown operation: {operation}"}
                
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"Invalid JSON: {str(e)}"
            }


class DataConverterTool(BaseTool):
    """Convert data between different formats"""
    
    @property
    def name(self):
        return "convert_data_format"
    
    @property
    def description(self):
        return "Converts data between different formats like JSON, CSV, XML, and YAML."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "Input data to convert"
                },
                "from_format": {
                    "type": "string",
                    "description": "Source format",
                    "enum": ["json", "csv", "xml", "yaml"]
                },
                "to_format": {
                    "type": "string",
                    "description": "Target format",
                    "enum": ["json", "csv", "xml", "yaml"]
                }
            },
            "required": ["data", "from_format", "to_format"]
        }
    
    def execute(self, data: str, from_format: str, to_format: str) -> dict:
        # Simulated conversion
        return {
            "from_format": from_format,
            "to_format": to_format,
            "converted_data": f"[Data converted from {from_format} to {to_format}]",
            "success": True
        }


# ============================================================================
# UTILITY TOOLS
# ============================================================================

class EmailValidatorTool(BaseTool):
    """Validate and extract information from email addresses"""
    
    @property
    def name(self):
        return "validate_email"
    
    @property
    def description(self):
        return "Validates email addresses and extracts information like domain, username, and checks for common patterns."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Email address to validate"
                },
                "check_dns": {
                    "type": "boolean",
                    "description": "Check if domain has valid MX records"
                }
            },
            "required": ["email"]
        }
    
    def execute(self, email: str, check_dns: bool = False) -> dict:
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(pattern, email))
        
        if is_valid:
            parts = email.split('@')
            username = parts[0]
            domain = parts[1]
            
            return {
                "email": email,
                "valid": True,
                "username": username,
                "domain": domain,
                "disposable": domain in ["tempmail.com", "throwaway.email"],
                "role_based": username in ["admin", "info", "support", "contact"]
            }
        else:
            return {
                "email": email,
                "valid": False,
                "error": "Invalid email format"
            }


class RandomGeneratorTool(BaseTool):
    """Generate random data for testing"""
    
    @property
    def name(self):
        return "generate_random_data"
    
    @property
    def description(self):
        return "Generates random data like numbers, strings, UUIDs, passwords, and test data."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "data_type": {
                    "type": "string",
                    "description": "Type of random data to generate",
                    "enum": ["number", "string", "uuid", "password", "email", "phone", "name"]
                },
                "count": {
                    "type": "integer",
                    "description": "Number of items to generate",
                    "minimum": 1,
                    "maximum": 100
                },
                "length": {
                    "type": "integer",
                    "description": "Length of generated string/password"
                },
                "min_value": {
                    "type": "number",
                    "description": "Minimum value for numbers"
                },
                "max_value": {
                    "type": "number",
                    "description": "Maximum value for numbers"
                }
            },
            "required": ["data_type"]
        }
    
    def execute(self, data_type: str, count: int = 1, length: int = 10,
                min_value: float = 0, max_value: float = 100) -> dict:
        import string
        import uuid
        
        results = []
        
        for _ in range(count):
            if data_type == "number":
                results.append(random.uniform(min_value, max_value))
            
            elif data_type == "string":
                chars = string.ascii_letters + string.digits
                results.append(''.join(random.choice(chars) for _ in range(length)))
            
            elif data_type == "uuid":
                results.append(str(uuid.uuid4()))
            
            elif data_type == "password":
                chars = string.ascii_letters + string.digits + string.punctuation
                results.append(''.join(random.choice(chars) for _ in range(length)))
            
            elif data_type == "email":
                username = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
                domain = random.choice(["example.com", "test.com", "mail.com"])
                results.append(f"{username}@{domain}")
            
            elif data_type == "phone":
                results.append(f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}")
            
            elif data_type == "name":
                first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana"]
                last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
                results.append(f"{random.choice(first_names)} {random.choice(last_names)}")
        
        return {
            "data_type": data_type,
            "count": count,
            "results": results if count > 1 else results[0]
        }
