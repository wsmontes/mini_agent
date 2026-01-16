"""Tests for tool implementations."""

import unittest
from tools import (
    CalculatorTool,
    SimpleCalculatorTool,
    WeatherTool,
    CurrentWeatherTool,
    ForecastWeatherTool,
    WebSearchTool,
    FileListTool
)


class TestCalculatorTools(unittest.TestCase):
    """Test calculator tools."""
    
    def test_calculator_addition(self):
        """Test addition."""
        calc = CalculatorTool()
        result = calc.execute("10 + 5")
        self.assertEqual(result["result"], 15)
        
    def test_calculator_complex(self):
        """Test complex expression."""
        calc = CalculatorTool()
        result = calc.execute("(2 + 3) * 4")
        self.assertEqual(result["result"], 20)
        
    def test_calculator_functions(self):
        """Test math functions."""
        calc = CalculatorTool()
        
        result = calc.execute("sqrt(25)")
        self.assertEqual(result["result"], 5.0)
        
        result = calc.execute("abs(-10)")
        self.assertEqual(result["result"], 10)
        
    def test_simple_calculator(self):
        """Test simple calculator."""
        calc = SimpleCalculatorTool()
        
        result = calc.execute("add", 5, 3)
        self.assertEqual(result["result"], 8)
        
        result = calc.execute("multiply", 4, 5)
        self.assertEqual(result["result"], 20)
        
        result = calc.execute("divide", 10, 2)
        self.assertEqual(result["result"], 5.0)


class TestWeatherTools(unittest.TestCase):
    """Test weather tools."""
    
    def test_weather_tool(self):
        """Test weather tool returns valid data."""
        weather = WeatherTool()
        result = weather.execute("London, UK")
        
        self.assertIn("temperature", result)
        self.assertIn("location", result)
        self.assertIn("conditions", result)
        
    def test_current_weather_tool(self):
        """Test current weather tool."""
        weather = CurrentWeatherTool()
        result = weather.execute("Paris, France")
        
        self.assertIn("temperature", result)
        self.assertEqual(result["location"], "Paris, France")
        
    def test_forecast_weather_tool(self):
        """Test forecast weather tool."""
        weather = ForecastWeatherTool()
        result = weather.execute("Tokyo, Japan", "2024-12-25")
        
        self.assertIn("temperature", result)
        self.assertEqual(result["date"], "2024-12-25")


class TestWebTools(unittest.TestCase):
    """Test web-related tools."""
    
    def test_web_search(self):
        """Test web search tool."""
        search = WebSearchTool()
        result = search.execute("Python programming", num_results=3)
        
        self.assertEqual(len(result["results"]), 3)
        self.assertIn("query", result)


class TestFileTools(unittest.TestCase):
    """Test file operation tools."""
    
    def test_list_directory(self):
        """Test directory listing."""
        file_list = FileListTool()
        result = file_list.execute(".")
        
        self.assertIn("files", result)
        self.assertIn("directories", result)


if __name__ == "__main__":
    unittest.main()
