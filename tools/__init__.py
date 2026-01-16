"""
Tools package - Contains all available tools for the agent.

Import tools:
    from tools import WeatherTool, CalculatorTool, WebSearchTool
    
Or import all:
    from tools import *
"""

from tools.base import BaseTool
from tools.weather import WeatherTool, CurrentWeatherTool, ForecastWeatherTool
from tools.calculator import CalculatorTool, SimpleCalculatorTool
from tools.web import WebSearchTool, WikipediaSearchTool, NewsSearchTool
from tools.file_ops import FileReadTool, FileWriteTool, FileListTool

# General purpose tools
from tools.general_tools import (
    GetWeatherTool,
    GetForecastTool,
    CurrencyConverterTool,
    StockPriceTool,
    AdvancedCalculatorTool,
    TextAnalysisTool,
    TranslateTool,
    DateTimeTool,
    WebSearchTool as GeneralWebSearchTool,
    URLFetchTool,
    GeocodeTool,
    DistanceCalculatorTool,
    JSONProcessorTool,
    DataConverterTool,
    EmailValidatorTool,
    RandomGeneratorTool
)

# Browser automation tools
from tools.browser_tools import (
    OpenURLTool,
    GetPageContentTool,
    ClickElementTool,
    FillFormTool,
    TakeScreenshotTool,
    ScrollPageTool,
    FindElementsTool,
    ExecuteJavaScriptTool,
    GoBackTool,
    GoForwardTool,
    CloseBrowserTool,
)

__all__ = [
    "BaseTool",
    # Original tools
    "WeatherTool",
    "CurrentWeatherTool",
    "ForecastWeatherTool",
    "CalculatorTool",
    "SimpleCalculatorTool",
    "WebSearchTool",
    "WikipediaSearchTool",
    "NewsSearchTool",
    "FileReadTool",
    "FileWriteTool",
    "FileListTool",
    # General purpose tools
    "GetWeatherTool",
    "GetForecastTool",
    "CurrencyConverterTool",
    "StockPriceTool",
    "AdvancedCalculatorTool",
    "TextAnalysisTool",
    "TranslateTool",
    "DateTimeTool",
    "GeneralWebSearchTool",
    "URLFetchTool",
    "GeocodeTool",
    "DistanceCalculatorTool",
    "JSONProcessorTool",
    "DataConverterTool",
    "EmailValidatorTool",
    "RandomGeneratorTool",
    # Browser automation tools
    "OpenURLTool",
    "GetPageContentTool",
    "ClickElementTool",
    "FillFormTool",
    "TakeScreenshotTool",
    "ScrollPageTool",
    "FindElementsTool",
    "ExecuteJavaScriptTool",
    "GoBackTool",
    "GoForwardTool",
    "CloseBrowserTool",
]
