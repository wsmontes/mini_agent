# Testing Guide

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_agent.py

# Run with coverage
python -m pytest --cov=. tests/

# Run with verbose output
python -m pytest -v tests/
```

## Using unittest

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test
python -m unittest tests.test_agent.TestQwenAgent

# Run with verbose output
python -m unittest discover -v tests/
```

## Test Structure

```
tests/
├── test_agent.py      # Agent core functionality
└── test_tools.py      # Tool implementations
```

## Writing New Tests

Example test case:

```python
import unittest
from agent import QwenAgent
from tools import MyCustomTool


class TestMyFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.agent = QwenAgent()
        
    def test_my_feature(self):
        """Test description."""
        # Arrange
        tool = MyCustomTool()
        
        # Act
        result = tool.execute(param="value")
        
        # Assert
        self.assertEqual(result["status"], "success")
```

## Mocking LM Studio

For tests that don't require actual API calls:

```python
from unittest.mock import Mock, patch

@patch('agent.OpenAI')
def test_with_mock(self, mock_openai):
    """Test with mocked OpenAI client."""
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    agent = QwenAgent()
    # Test agent behavior
```

## Test Coverage

Aim for:
- Core functionality: 80%+ coverage
- Tool implementations: 70%+ coverage
- Edge cases: Include error handling tests

## CI/CD Integration

Add to GitHub Actions:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/
```
