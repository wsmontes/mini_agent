"""
General Tools Demonstration
Shows how to use the comprehensive set of general-purpose tools
"""

import sys
sys.path.insert(0, '.')

from agent import QwenAgent
from tools.general_tools import (
    GetWeatherTool,
    GetForecastTool,
    CurrencyConverterTool,
    StockPriceTool,
    AdvancedCalculatorTool,
    TextAnalysisTool,
    TranslateTool,
    DateTimeTool,
    URLFetchTool,
    GeocodeTool,
    DistanceCalculatorTool,
    JSONProcessorTool,
    DataConverterTool,
    EmailValidatorTool,
    RandomGeneratorTool
)

def demo_weather_tools():
    """Demonstrate weather-related tools"""
    print("\n" + "="*60)
    print("WEATHER TOOLS DEMO")
    print("="*60)
    
    agent = QwenAgent()
    agent.register_tool(GetWeatherTool())
    agent.register_tool(GetForecastTool())
    
    # Test weather queries
    queries = [
        "What's the weather in Tokyo?",
        "Give me a 7-day forecast for Paris",
        "Tell me the temperature in New York in Fahrenheit"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = agent.query(query)
        print(f"Response: {response}\n")


def demo_financial_tools():
    """Demonstrate financial tools"""
    print("\n" + "="*60)
    print("FINANCIAL TOOLS DEMO")
    print("="*60)
    
    agent = QwenAgent()
    agent.register_tool(CurrencyConverterTool())
    agent.register_tool(StockPriceTool())
    
    queries = [
        "Convert 1000 USD to EUR",
        "What's the current price of Apple stock?",
        "Convert 500 BRL to JPY",
        "Get detailed stock information for TSLA"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = agent.query(query)
        print(f"Response: {response}\n")


def demo_math_tools():
    """Demonstrate mathematical tools"""
    print("\n" + "="*60)
    print("MATHEMATICAL TOOLS DEMO")
    print("="*60)
    
    agent = QwenAgent()
    agent.register_tool(AdvancedCalculatorTool())
    
    queries = [
        "Calculate the factorial of 10",
        "What is the square root of 144?",
        "Calculate 2 to the power of 8",
        "Find the mean of these numbers: 10, 20, 30, 40, 50",
        "Calculate the standard deviation of [5, 10, 15, 20, 25]"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = agent.query(query)
        print(f"Response: {response}\n")


def demo_text_tools():
    """Demonstrate text processing tools"""
    print("\n" + "="*60)
    print("TEXT PROCESSING TOOLS DEMO")
    print("="*60)
    
    agent = QwenAgent()
    agent.register_tool(TextAnalysisTool())
    agent.register_tool(TranslateTool())
    
    queries = [
        "Analyze this text: 'Python is an amazing programming language. It's versatile and powerful.'",
        "Count the words in: 'The quick brown fox jumps over the lazy dog'",
        "Analyze the sentiment of: 'This is a great product! I love it!'",
        "Translate 'Hello world' to Spanish"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = agent.query(query)
        print(f"Response: {response}\n")


def demo_datetime_tools():
    """Demonstrate date and time tools"""
    print("\n" + "="*60)
    print("DATE & TIME TOOLS DEMO")
    print("="*60)
    
    agent = QwenAgent()
    agent.register_tool(DateTimeTool())
    
    queries = [
        "What's the current date and time?",
        "Add 30 days to today's date",
        "What was the date 90 days ago?",
        "Format today's date in long format"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = agent.query(query)
        print(f"Response: {response}\n")


def demo_location_tools():
    """Demonstrate location and geography tools"""
    print("\n" + "="*60)
    print("LOCATION TOOLS DEMO")
    print("="*60)
    
    agent = QwenAgent()
    agent.register_tool(GeocodeTool())
    agent.register_tool(DistanceCalculatorTool())
    
    queries = [
        "Get coordinates for Times Square, New York",
        "What's the distance between New York (40.7128, -74.0060) and Los Angeles (34.0522, -118.2437)?",
        "Geocode the address: 1600 Amphitheatre Parkway, Mountain View, CA"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = agent.query(query)
        print(f"Response: {response}\n")


def demo_data_tools():
    """Demonstrate data processing tools"""
    print("\n" + "="*60)
    print("DATA PROCESSING TOOLS DEMO")
    print("="*60)
    
    agent = QwenAgent()
    agent.register_tool(JSONProcessorTool())
    agent.register_tool(DataConverterTool())
    
    queries = [
        'Validate this JSON: {"name": "John", "age": 30}',
        'Pretty print this JSON: {"a":1,"b":2,"c":3}',
        'Extract keys from: {"user": "admin", "role": "admin", "active": true}'
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = agent.query(query)
        print(f"Response: {response}\n")


def demo_utility_tools():
    """Demonstrate utility tools"""
    print("\n" + "="*60)
    print("UTILITY TOOLS DEMO")
    print("="*60)
    
    agent = QwenAgent()
    agent.register_tool(EmailValidatorTool())
    agent.register_tool(RandomGeneratorTool())
    
    queries = [
        "Validate this email: john.doe@example.com",
        "Is admin@company.co.uk a valid email?",
        "Generate 5 random numbers between 1 and 100",
        "Create a random password with 16 characters",
        "Generate 3 random email addresses"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = agent.query(query)
        print(f"Response: {response}\n")


def demo_all_categories():
    """Run comprehensive demo with all tool categories"""
    print("\n" + "="*60)
    print("COMPREHENSIVE AGENT DEMO - ALL TOOLS")
    print("="*60)
    
    # Create agent with ALL tools
    agent = QwenAgent()
    
    # Register all tools
    tools = [
        GetWeatherTool(),
        GetForecastTool(),
        CurrencyConverterTool(),
        StockPriceTool(),
        AdvancedCalculatorTool(),
        TextAnalysisTool(),
        TranslateTool(),
        DateTimeTool(),
        URLFetchTool(),
        GeocodeTool(),
        DistanceCalculatorTool(),
        JSONProcessorTool(),
        DataConverterTool(),
        EmailValidatorTool(),
        RandomGeneratorTool()
    ]
    
    for tool in tools:
        agent.register_tool(tool)
    
    print(f"\nAgent initialized with {len(tools)} tools")
    print("Available tools:", [tool.name for tool in tools])
    
    # Complex multi-tool queries
    complex_queries = [
        "What's the weather in London and convert 100 GBP to USD?",
        "Calculate the factorial of 5 and tell me the current time",
        "Validate email test@example.com and generate a random password",
        "Get stock price for AAPL and calculate the mean of [10, 20, 30]",
        "What's the distance between coordinates (0,0) and (10,10) in km and add 7 days to today?"
    ]
    
    for query in complex_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        response = agent.query(query)
        print(f"Response: {response}\n")


def interactive_demo():
    """Interactive demo where user can ask questions"""
    print("\n" + "="*60)
    print("INTERACTIVE DEMO - ASK ME ANYTHING!")
    print("="*60)
    print("Available tool categories:")
    print("  • Weather & Climate")
    print("  • Finance (Currency, Stocks)")
    print("  • Mathematics (Advanced calculations)")
    print("  • Text Processing (Analysis, Translation)")
    print("  • Date & Time")
    print("  • Location & Geography")
    print("  • Data Processing (JSON, Data conversion)")
    print("  • Utilities (Email validation, Random generation)")
    print("\nType 'exit' to quit\n")
    
    # Setup agent with all tools
    agent = QwenAgent()
    tools = [
        GetWeatherTool(),
        GetForecastTool(),
        CurrencyConverterTool(),
        StockPriceTool(),
        AdvancedCalculatorTool(),
        TextAnalysisTool(),
        TranslateTool(),
        DateTimeTool(),
        URLFetchTool(),
        GeocodeTool(),
        DistanceCalculatorTool(),
        JSONProcessorTool(),
        DataConverterTool(),
        EmailValidatorTool(),
        RandomGeneratorTool()
    ]
    
    for tool in tools:
        agent.register_tool(tool)
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            print("\nProcessing...")
            response = agent.query(query)
            print(f"\nResponse: {response}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="General Tools Demonstration")
    parser.add_argument(
        '--demo',
        choices=['weather', 'finance', 'math', 'text', 'datetime', 'location', 'data', 'utility', 'all', 'interactive'],
        default='all',
        help="Choose which demo to run"
    )
    
    args = parser.parse_args()
    
    demos = {
        'weather': demo_weather_tools,
        'finance': demo_financial_tools,
        'math': demo_math_tools,
        'text': demo_text_tools,
        'datetime': demo_datetime_tools,
        'location': demo_location_tools,
        'data': demo_data_tools,
        'utility': demo_utility_tools,
        'all': demo_all_categories,
        'interactive': interactive_demo
    }
    
    demos[args.demo]()
