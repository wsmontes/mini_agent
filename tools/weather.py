"""Weather tool for getting temperature and weather information."""

from typing import Dict, Any
from datetime import datetime, timedelta
import random
from tools.base import BaseTool


class WeatherTool(BaseTool):
    """Get current or historical weather information for a location."""
    
    name = "get_weather"
    description = (
        "Get weather information (temperature, conditions) for a specific location. "
        "Can get current weather or weather for a specific date."
    )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City, State, Country (e.g., 'San Francisco, CA, USA')"
                },
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format. Omit for current weather."
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit (default: celsius)"
                }
            },
            "required": ["location"]
        }
        
    def execute(self, location: str, date: str = None, unit: str = "celsius") -> Dict[str, Any]:
        """
        Get weather for a location.
        
        Note: This is a simulation. In production, integrate with:
        - OpenWeatherMap API
        - Weather.gov API
        - AccuWeather API
        """
        # Simulate weather data
        base_temp_c = random.uniform(10, 30)
        
        # Adjust for date if provided
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
                days_diff = (target_date - datetime.now()).days
                base_temp_c += random.uniform(-2, 2) * abs(days_diff) * 0.1
            except ValueError:
                return {
                    "error": f"Invalid date format: {date}. Use YYYY-MM-DD"
                }
                
        # Convert unit if needed
        if unit == "fahrenheit":
            temperature = base_temp_c * 9/5 + 32
        else:
            temperature = base_temp_c
            
        # Random conditions
        conditions = random.choice([
            "Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Sunny"
        ])
        
        result = {
            "location": location,
            "temperature": round(temperature, 1),
            "unit": unit,
            "conditions": conditions,
            "humidity": random.randint(40, 80),
            "wind_speed": round(random.uniform(5, 25), 1)
        }
        
        if date:
            result["date"] = date
        else:
            result["date"] = datetime.now().strftime("%Y-%m-%d")
            result["time"] = datetime.now().strftime("%H:%M")
            
        return result


class CurrentWeatherTool(BaseTool):
    """Simplified tool for current weather only."""
    
    name = "get_current_temperature"
    description = "Get the current temperature for a specific location"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City, State, Country format (e.g., 'San Francisco, CA, USA')"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit (default: celsius)"
                }
            },
            "required": ["location"]
        }
        
    def execute(self, location: str, unit: str = "celsius") -> Dict[str, Any]:
        """Get current temperature."""
        base_temp_c = random.uniform(15, 28)
        
        if unit == "fahrenheit":
            temperature = base_temp_c * 9/5 + 32
        else:
            temperature = base_temp_c
            
        return {
            "temperature": round(temperature, 1),
            "location": location,
            "unit": unit
        }


class ForecastWeatherTool(BaseTool):
    """Get weather forecast for a specific date."""
    
    name = "get_temperature_date"
    description = "Get the temperature for a specific date and location"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City, State, Country format"
                },
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit (default: celsius)"
                }
            },
            "required": ["location", "date"]
        }
        
    def execute(self, location: str, date: str, unit: str = "celsius") -> Dict[str, Any]:
        """Get temperature for a specific date."""
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"error": f"Invalid date format: {date}"}
            
        base_temp_c = random.uniform(15, 28)
        
        if unit == "fahrenheit":
            temperature = base_temp_c * 9/5 + 32
        else:
            temperature = base_temp_c
            
        return {
            "temperature": round(temperature, 1),
            "location": location,
            "date": date,
            "unit": unit
        }
