"""Unit tests for agent functionality."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from agent import QwenAgent
from tools import CalculatorTool, WeatherTool


class TestQwenAgent(unittest.TestCase):
    """Test cases for QwenAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = QwenAgent(
            base_url="http://localhost:1234/v1",
            api_key="test-key",
            auto_execute_tools=True
        )
        
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.base_url, "http://localhost:1234/v1")
        self.assertEqual(self.agent.api_key, "test-key")
        self.assertTrue(self.agent.auto_execute_tools)
        
    def test_register_tool(self):
        """Test tool registration."""
        calc_tool = CalculatorTool()
        self.agent.register_tool(calc_tool)
        
        self.assertIn("calculator", self.agent.tools)
        self.assertEqual(len(self.agent.tool_schemas), 1)
        
    def test_unregister_tool(self):
        """Test tool removal."""
        calc_tool = CalculatorTool()
        self.agent.register_tool(calc_tool)
        self.agent.unregister_tool("calculator")
        
        self.assertNotIn("calculator", self.agent.tools)
        self.assertEqual(len(self.agent.tool_schemas), 0)
        
    def test_clear_tools(self):
        """Test clearing all tools."""
        self.agent.register_tool(CalculatorTool())
        self.agent.register_tool(WeatherTool())
        self.agent.clear_tools()
        
        self.assertEqual(len(self.agent.tools), 0)
        self.assertEqual(len(self.agent.tool_schemas), 0)
        
    def test_set_system_message(self):
        """Test setting system message."""
        message = "You are a helpful assistant"
        self.agent.set_system_message(message)
        
        self.assertEqual(self.agent.system_message, message)
        
    def test_reset_conversation(self):
        """Test conversation reset."""
        self.agent.messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"}
        ]
        self.agent.reset_conversation()
        
        self.assertEqual(len(self.agent.messages), 0)
        
    def test_prepare_messages_with_system(self):
        """Test message preparation with system message."""
        self.agent.set_system_message("System message")
        self.agent.messages = [{"role": "user", "content": "Test"}]
        
        messages = self.agent._prepare_messages()
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")


class TestToolExecution(unittest.TestCase):
    """Test cases for tool execution."""
    
    def test_calculator_tool_basic(self):
        """Test basic calculator operations."""
        calc = CalculatorTool()
        
        result = calc.execute("2 + 2")
        self.assertEqual(result["result"], 4)
        
        result = calc.execute("sqrt(16)")
        self.assertEqual(result["result"], 4.0)
        
    def test_calculator_tool_invalid(self):
        """Test calculator with invalid input."""
        calc = CalculatorTool()
        
        result = calc.execute("invalid")
        self.assertIn("error", result)
        
        result = calc.execute("1 / 0")
        self.assertIn("error", result)
        
    def test_weather_tool(self):
        """Test weather tool."""
        weather = WeatherTool()
        
        result = weather.execute("San Francisco, CA, USA")
        
        self.assertIn("temperature", result)
        self.assertIn("location", result)
        self.assertEqual(result["unit"], "celsius")
        
    def test_weather_tool_with_date(self):
        """Test weather tool with date."""
        weather = WeatherTool()
        
        result = weather.execute(
            "New York, NY, USA",
            date="2024-12-25"
        )
        
        self.assertIn("date", result)
        self.assertEqual(result["date"], "2024-12-25")


if __name__ == "__main__":
    unittest.main()
