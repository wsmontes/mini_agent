# General Purpose Tools - Complete Reference

This document provides a comprehensive overview of all general-purpose tools available in the mini_agent system, designed to be compatible with the Qwen3-4B-toolcalling model trained on the xlam-function-calling-60k dataset.

## 📑 Table of Contents

1. [Weather & Climate Tools](#weather--climate-tools)
2. [Financial Tools](#financial-tools)
3. [Mathematical Tools](#mathematical-tools)
4. [Text Processing Tools](#text-processing-tools)
5. [Date & Time Tools](#date--time-tools)
6. [Web & Search Tools](#web--search-tools)
7. [Location & Geography Tools](#location--geography-tools)
8. [Data Processing Tools](#data-processing-tools)
9. [Utility Tools](#utility-tools)
10. [Usage Examples](#usage-examples)

---

## Weather & Climate Tools

### 🌤️ GetWeatherTool

**Tool Name:** `get_weather`

Fetches current weather information for any location worldwide.

**Parameters:**
- `location` (string, required): City name, address, or coordinates
- `units` (string, optional): Temperature unit - 'celsius', 'fahrenheit', or 'kelvin'

**Returns:**
```json
{
  "location": "New York",
  "temperature": 22.5,
  "units": "celsius",
  "condition": "sunny",
  "humidity": 65,
  "wind_speed": 15,
  "timestamp": "2024-01-01T12:00:00"
}
```

**Example Queries:**
- "What's the weather in London?"
- "Get temperature in Tokyo in Fahrenheit"
- "Tell me the current weather conditions in Paris"

---

### 📅 GetForecastTool

**Tool Name:** `get_forecast`

Retrieves weather forecast for multiple days (up to 14 days).

**Parameters:**
- `location` (string, required): City name or coordinates
- `days` (integer, required): Number of days (1-14)
- `units` (string, optional): Temperature unit

**Returns:**
```json
{
  "location": "Paris",
  "units": "celsius",
  "forecast": [
    {
      "date": "2024-01-01",
      "temperature": 18.5,
      "condition": "cloudy",
      "precipitation_chance": 30
    }
  ]
}
```

**Example Queries:**
- "Give me a 7-day forecast for San Francisco"
- "What will the weather be like in Berlin next week?"

---

## Financial Tools

### 💱 CurrencyConverterTool

**Tool Name:** `convert_currency`

Converts amounts between different currencies using current exchange rates.

**Parameters:**
- `amount` (number, required): Amount to convert
- `from_currency` (string, required): Source currency code (e.g., 'USD', 'EUR')
- `to_currency` (string, required): Target currency code

**Supported Currencies:**
USD, EUR, GBP, JPY, BRL, CAD, AUD, CNY

**Returns:**
```json
{
  "original_amount": 100,
  "from_currency": "USD",
  "to_currency": "EUR",
  "converted_amount": 85.00,
  "exchange_rate": 0.85,
  "timestamp": "2024-01-01T12:00:00"
}
```

**Example Queries:**
- "Convert 1000 USD to EUR"
- "How much is 500 GBP in JPY?"
- "Exchange 2000 BRL to CAD"

---

### 📈 StockPriceTool

**Tool Name:** `get_stock_price`

Retrieves current stock price and information for any ticker symbol.

**Parameters:**
- `ticker` (string, required): Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
- `include_details` (boolean, optional): Include volume, market cap, etc.

**Returns:**
```json
{
  "ticker": "AAPL",
  "price": 175.50,
  "change": 2.30,
  "change_percent": 1.33,
  "timestamp": "2024-01-01T16:00:00",
  "volume": 45000000,
  "market_cap": "$2.8T",
  "52_week_high": 198.23,
  "52_week_low": 124.17
}
```

**Example Queries:**
- "What's the current price of Apple stock?"
- "Get Tesla stock price with details"
- "How is Microsoft stock performing?"

---

## Mathematical Tools

### 🔢 AdvancedCalculatorTool

**Tool Name:** `advanced_calculator`

Performs advanced mathematical operations including trigonometry, logarithms, and statistics.

**Parameters:**
- `operation` (string, required): Operation type
- `values` (array of numbers, required): Input values

**Supported Operations:**
- `factorial`: Calculate n! (requires 1 value)
- `power`: Calculate x^y (requires 2 values)
- `sqrt`: Square root (requires 1 value)
- `log`: Logarithm (requires 1-2 values)
- `sin`, `cos`, `tan`: Trigonometric functions (requires 1 value in degrees)
- `mean`: Average of numbers
- `median`: Middle value
- `std_dev`: Standard deviation

**Returns:**
```json
{
  "operation": "factorial",
  "input": [10],
  "result": 3628800
}
```

**Example Queries:**
- "Calculate the factorial of 10"
- "What is 2 to the power of 8?"
- "Find the mean of [10, 20, 30, 40, 50]"
- "Calculate standard deviation of [5, 10, 15, 20]"
- "What is the sine of 45 degrees?"

---

## Text Processing Tools

### 📝 TextAnalysisTool

**Tool Name:** `analyze_text`

Analyzes text for various metrics including word count, sentiment, and readability.

**Parameters:**
- `text` (string, required): Text to analyze
- `metrics` (array, optional): Specific metrics to calculate

**Available Metrics:**
- `word_count`: Total words
- `char_count`: Total characters
- `sentence_count`: Number of sentences
- `avg_word_length`: Average word length
- `sentiment`: Sentiment analysis (positive/negative/neutral)

**Returns:**
```json
{
  "word_count": 25,
  "char_count": 150,
  "char_count_no_spaces": 125,
  "sentence_count": 3,
  "avg_word_length": 5.2,
  "sentiment": "positive",
  "sentiment_score": {
    "positive": 3,
    "negative": 0
  }
}
```

**Example Queries:**
- "Analyze this text: 'Python is amazing!'"
- "Count words in 'The quick brown fox jumps over the lazy dog'"
- "What's the sentiment of 'I love this product!'"

---

### 🌐 TranslateTool

**Tool Name:** `translate_text`

Translates text between different languages.

**Parameters:**
- `text` (string, required): Text to translate
- `target_language` (string, required): Target language code
- `source_language` (string, optional): Source language (default: auto-detect)

**Supported Languages:**
en, es, fr, de, pt, it, ja, zh, ko, ru

**Returns:**
```json
{
  "original_text": "Hello world",
  "translated_text": "Hola mundo",
  "source_language": "en",
  "target_language": "es",
  "confidence": 0.95
}
```

**Example Queries:**
- "Translate 'Hello world' to Spanish"
- "Convert 'Bonjour' to English"
- "How do you say 'Thank you' in German?"

---

## Date & Time Tools

### 🕐 DateTimeTool

**Tool Name:** `datetime_operations`

Performs various date and time operations including conversions and calculations.

**Parameters:**
- `operation` (string, required): Operation type
- `date` (string, optional): Date in ISO format (YYYY-MM-DD)
- `value` (integer, optional): Numeric value for calculations
- `format` (string, optional): Output format
- `timezone` (string, optional): Timezone name

**Supported Operations:**
- `current_time`: Get current date and time
- `add_days`: Add days to a date
- `subtract_days`: Subtract days from a date
- `format_date`: Format date in different styles
- `time_difference`: Calculate difference between dates
- `timezone_convert`: Convert between timezones

**Returns:**
```json
{
  "datetime": "2024-01-01T12:00:00",
  "date": "2024-01-01",
  "time": "12:00:00",
  "timestamp": 1704110400
}
```

**Example Queries:**
- "What's the current date and time?"
- "Add 30 days to today"
- "What was the date 90 days ago?"
- "Format today in long format"

---

## Web & Search Tools

### 🔍 WebSearchTool

**Tool Name:** `web_search`

Searches the web for information and returns relevant results.

**Parameters:**
- `query` (string, required): Search query
- `num_results` (integer, optional): Number of results (1-20, default: 10)
- `language` (string, optional): Language code (default: 'en')

**Returns:**
```json
{
  "query": "Python programming",
  "num_results": 5,
  "language": "en",
  "results": [
    {
      "title": "Python.org",
      "url": "https://python.org",
      "snippet": "Official Python website...",
      "position": 1
    }
  ]
}
```

**Example Queries:**
- "Search for Python tutorials"
- "Find information about machine learning"
- "Look up latest AI news"

---

### 🌐 URLFetchTool

**Tool Name:** `fetch_url`

Fetches content from a URL and extracts specific elements.

**Parameters:**
- `url` (string, required): URL to fetch
- `extract` (string, optional): What to extract ('text', 'title', 'links', 'images', 'metadata', 'all')
- `timeout` (integer, optional): Request timeout in seconds

**Returns:**
```json
{
  "url": "https://example.com",
  "status_code": 200,
  "title": "Example Domain",
  "text": "This domain is for use in examples...",
  "links": ["https://example.com/page1"],
  "images": ["https://example.com/image.jpg"]
}
```

**Example Queries:**
- "Fetch content from https://example.com"
- "Get all links from a webpage"
- "Extract title from https://python.org"

---

## Location & Geography Tools

### 📍 GeocodeTool

**Tool Name:** `geocode`

Converts addresses to coordinates (geocoding) or coordinates to addresses (reverse geocoding).

**Parameters:**
- `address` (string, optional): Address to geocode
- `latitude` (number, optional): Latitude for reverse geocoding
- `longitude` (number, optional): Longitude for reverse geocoding
- `reverse` (boolean, optional): Use reverse geocoding

**Returns:**
```json
{
  "address": "Times Square, New York",
  "latitude": 40.7580,
  "longitude": -73.9855,
  "confidence": 0.95
}
```

**Example Queries:**
- "Get coordinates for Times Square, New York"
- "What's the latitude and longitude of the Eiffel Tower?"
- "Reverse geocode coordinates 40.7128, -74.0060"

---

### 📏 DistanceCalculatorTool

**Tool Name:** `calculate_distance`

Calculates distance between two geographic points.

**Parameters:**
- `origin_lat` (number, required): Origin latitude
- `origin_lon` (number, required): Origin longitude
- `dest_lat` (number, required): Destination latitude
- `dest_lon` (number, required): Destination longitude
- `unit` (string, optional): Unit ('km', 'miles', 'meters')

**Returns:**
```json
{
  "origin": {"latitude": 40.7128, "longitude": -74.0060},
  "destination": {"latitude": 34.0522, "longitude": -118.2437},
  "distance": 3936.42,
  "unit": "km"
}
```

**Example Queries:**
- "Calculate distance between New York (40.7128, -74.0060) and LA (34.0522, -118.2437)"
- "How far is it from Paris to London?"

---

## Data Processing Tools

### 📋 JSONProcessorTool

**Tool Name:** `process_json`

Processes JSON data with various operations.

**Parameters:**
- `json_data` (string, required): JSON string to process
- `operation` (string, required): Operation type
- `path` (string, optional): JSON path for extraction

**Supported Operations:**
- `validate`: Check if JSON is valid
- `pretty_print`: Format JSON with indentation
- `minify`: Remove whitespace
- `extract_keys`: Get all keys
- `get_value`: Extract value by path

**Returns:**
```json
{
  "valid": true,
  "message": "JSON is valid",
  "formatted": "{\n  \"name\": \"John\"\n}"
}
```

**Example Queries:**
- "Validate this JSON: {\"name\": \"John\"}"
- "Pretty print {\"a\":1,\"b\":2}"
- "Extract keys from JSON data"

---

### 🔄 DataConverterTool

**Tool Name:** `convert_data_format`

Converts data between different formats (JSON, CSV, XML, YAML).

**Parameters:**
- `data` (string, required): Input data
- `from_format` (string, required): Source format
- `to_format` (string, required): Target format

**Supported Formats:**
json, csv, xml, yaml

**Returns:**
```json
{
  "from_format": "json",
  "to_format": "csv",
  "converted_data": "[Converted data]",
  "success": true
}
```

**Example Queries:**
- "Convert this JSON to CSV"
- "Transform XML to JSON format"

---

## Utility Tools

### ✉️ EmailValidatorTool

**Tool Name:** `validate_email`

Validates email addresses and extracts information.

**Parameters:**
- `email` (string, required): Email to validate
- `check_dns` (boolean, optional): Check DNS records

**Returns:**
```json
{
  "email": "john@example.com",
  "valid": true,
  "username": "john",
  "domain": "example.com",
  "disposable": false,
  "role_based": false
}
```

**Example Queries:**
- "Validate email john.doe@example.com"
- "Is admin@company.com a valid email?"
- "Check if test@tempmail.com is disposable"

---

### 🎲 RandomGeneratorTool

**Tool Name:** `generate_random_data`

Generates random data for testing and development.

**Parameters:**
- `data_type` (string, required): Type of data to generate
- `count` (integer, optional): Number of items (1-100)
- `length` (integer, optional): Length for strings/passwords
- `min_value` (number, optional): Minimum for numbers
- `max_value` (number, optional): Maximum for numbers

**Supported Types:**
- `number`: Random numbers
- `string`: Random strings
- `uuid`: UUID v4
- `password`: Secure passwords
- `email`: Random email addresses
- `phone`: Phone numbers
- `name`: Random names

**Returns:**
```json
{
  "data_type": "password",
  "count": 1,
  "results": "aB3$xY9@mP2!"
}
```

**Example Queries:**
- "Generate 5 random numbers"
- "Create a random 16-character password"
- "Generate 3 test email addresses"
- "Give me a random UUID"

---

## Usage Examples

### Basic Usage

```python
from agent import QwenAgent
from tools.general_tools import GetWeatherTool, CurrencyConverterTool

# Create agent
agent = QwenAgent()

# Register tools
agent.register_tool(GetWeatherTool())
agent.register_tool(CurrencyConverterTool())

# Make queries
response = agent.query("What's the weather in Paris?")
print(response)

response = agent.query("Convert 100 USD to EUR")
print(response)
```

### Multi-Tool Query

```python
from agent import QwenAgent
from tools.general_tools import *

# Create agent with multiple tools
agent = QwenAgent()
agent.register_tool(GetWeatherTool())
agent.register_tool(CurrencyConverterTool())
agent.register_tool(AdvancedCalculatorTool())

# Complex query using multiple tools
response = agent.query(
    "What's the weather in London, convert 1000 GBP to USD, "
    "and calculate the factorial of 10"
)
print(response)
```

### Running the Demo

```bash
# Run all demos
python examples/general_tools_demo.py --demo all

# Run specific category demo
python examples/general_tools_demo.py --demo weather
python examples/general_tools_demo.py --demo finance
python examples/general_tools_demo.py --demo math

# Interactive mode
python examples/general_tools_demo.py --demo interactive
```

---

## Tool Categories Summary

| Category | Tools | Use Cases |
|----------|-------|-----------|
| **Weather** | 2 tools | Current weather, forecasts |
| **Finance** | 2 tools | Currency conversion, stock prices |
| **Math** | 1 tool | Advanced calculations, statistics |
| **Text** | 2 tools | Text analysis, translation |
| **DateTime** | 1 tool | Date calculations, formatting |
| **Web** | 2 tools | Web search, URL fetching |
| **Location** | 2 tools | Geocoding, distance calculation |
| **Data** | 2 tools | JSON processing, format conversion |
| **Utility** | 2 tools | Email validation, random data |

**Total: 16 comprehensive tools for general-purpose use**

---

## Dataset Compatibility

These tools are designed to be compatible with the **xlam-function-calling-60k dataset** used to train the Qwen3-4B-toolcalling model. The tool definitions follow the same schema format:

```json
{
  "name": "tool_name",
  "description": "Tool description",
  "parameters": {
    "type": "object",
    "properties": {
      "param_name": {
        "type": "string",
        "description": "Parameter description"
      }
    },
    "required": ["param_name"]
  }
}
```

This ensures optimal performance and compatibility with the model's training.

---

## Best Practices

1. **Clear Queries**: Use natural language that clearly indicates which tool to use
2. **Specific Parameters**: Provide all required information in your query
3. **Tool Combination**: The agent can use multiple tools in a single query
4. **Error Handling**: All tools include error handling for invalid inputs
5. **Testing**: Use the demo script to test tools before integration

---

## Contributing

To add new tools:

1. Create tool class inheriting from `BaseTool`
2. Implement `name`, `description`, `get_parameters()`, and `execute()` methods
3. Add to `tools/general_tools.py`
4. Update `tools/__init__.py` exports
5. Add demo examples

---

## Support

For issues or questions:
- Check existing examples in `/examples/`
- Review tool documentation above
- Test with `general_tools_demo.py`

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Compatible with**: Qwen3-4B-toolcalling model
