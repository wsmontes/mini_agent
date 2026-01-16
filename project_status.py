#!/usr/bin/env python3
"""
Project Status and Statistics
Run this to see project overview and verify setup
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def count_files(pattern):
    """Count files matching pattern."""
    path = Path(".")
    return len(list(path.rglob(pattern)))

def count_lines(pattern):
    """Count lines in files matching pattern."""
    path = Path(".")
    total = 0
    for file_path in path.rglob(pattern):
        if ".git" not in str(file_path) and "venv" not in str(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total += len(f.readlines())
            except:
                pass
    return total

def check_file_exists(filepath):
    """Check if file exists."""
    return "✓" if Path(filepath).exists() else "✗"

def check_directory(dirpath):
    """Check directory and count files."""
    path = Path(dirpath)
    if path.exists():
        files = len([f for f in path.iterdir() if f.is_file()])
        return f"✓ ({files} files)"
    return "✗"

def main():
    print_header("Mini Agent - Project Status")
    
    # Project stats
    print("\n📊 Project Statistics:")
    print(f"  Python files:      {count_files('*.py')}")
    print(f"  Documentation:     {count_files('*.md')}")
    print(f"  Total files:       {count_files('*.py') + count_files('*.md') + count_files('*.txt')}")
    print(f"  Lines of Python:   {count_lines('*.py'):,}")
    print(f"  Lines of docs:     {count_lines('*.md'):,}")
    
    # Core files
    print_header("Core Components")
    print(f"  agent.py:          {check_file_exists('agent.py')}")
    print(f"  main.py:           {check_file_exists('main.py')}")
    print(f"  requirements.txt:  {check_file_exists('requirements.txt')}")
    print(f"  setup.sh:          {check_file_exists('setup.sh')}")
    print(f"  .env.example:      {check_file_exists('.env.example')}")
    
    # Directories
    print_header("Project Structure")
    print(f"  tools/:            {check_directory('tools')}")
    print(f"  examples/:         {check_directory('examples')}")
    print(f"  tests/:            {check_directory('tests')}")
    print(f"  docs/:             {check_directory('docs')}")
    
    # Documentation
    print_header("Documentation")
    print(f"  README.md:         {check_file_exists('README.md')}")
    print(f"  QUICKSTART.md:     {check_file_exists('QUICKSTART.md')}")
    print(f"  SUMMARY.md:        {check_file_exists('SUMMARY.md')}")
    print(f"  FAQ.md:            {check_file_exists('FAQ.md')}")
    print(f"  PROJECT_STRUCTURE: {check_file_exists('PROJECT_STRUCTURE.md')}")
    
    # Tools
    print_header("Built-in Tools")
    tools = {
        "base.py": "Base tool class",
        "calculator.py": "Math calculations",
        "weather.py": "Weather information",
        "web.py": "Web search",
        "file_ops.py": "File operations"
    }
    for tool_file, desc in tools.items():
        status = check_file_exists(f"tools/{tool_file}")
        print(f"  {tool_file:18} {status}  {desc}")
    
    # Examples
    print_header("Example Scripts")
    examples = [
        "simple_usage.py",
        "weather_demo.py",
        "calculator_demo.py",
        "multi_tool_demo.py",
        "custom_tool.py"
    ]
    for example in examples:
        status = check_file_exists(f"examples/{example}")
        print(f"  {example:25} {status}")
    
    # Tests
    print_header("Tests")
    print(f"  test_agent.py:     {check_file_exists('tests/test_agent.py')}")
    print(f"  test_tools.py:     {check_file_exists('tests/test_tools.py')}")
    print(f"  tests/README.md:   {check_file_exists('tests/README.md')}")
    
    # Environment check
    print_header("Environment Check")
    
    # Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 11)
    print(f"  Python version:    {py_version} {'✓' if py_ok else '✗ (need 3.11+)'}")
    
    # Virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"  Virtual env:       {'✓ Active' if in_venv else '✗ Not active'}")
    
    # Dependencies
    try:
        import openai
        print(f"  openai:            ✓ {openai.__version__}")
    except ImportError:
        print(f"  openai:            ✗ Not installed")
    
    try:
        import dotenv
        print(f"  python-dotenv:     ✓")
    except ImportError:
        print(f"  python-dotenv:     ✗ Not installed")
    
    try:
        import rich
        print(f"  rich:              ✓")
    except ImportError:
        print(f"  rich:              ✗ Not installed")
    
    # .env file
    env_exists = Path(".env").exists()
    print(f"  .env file:         {'✓' if env_exists else '✗ (copy from .env.example)'}")
    
    # Recommendations
    print_header("Next Steps")
    
    if not env_exists:
        print("  1. Copy .env.example to .env")
        print("     cp .env.example .env")
    
    if not in_venv:
        print("  2. Activate virtual environment")
        print("     source venv/bin/activate")
    
    if not py_ok:
        print("  3. Upgrade Python to 3.11+")
    
    try:
        import openai, dotenv, rich
    except ImportError:
        print("  4. Install dependencies")
        print("     pip install -r requirements.txt")
    
    print("\n  5. Setup LM Studio")
    print("     - Download from lmstudio.ai")
    print("     - Load Qwen3-4B-toolcalling model")
    print("     - Start local server")
    
    print("\n  6. Run the agent")
    print("     python main.py")
    
    print("\n  7. Try examples")
    print("     python examples/weather_demo.py")
    
    print_header("Project Ready! ✨")
    print("\n  Read QUICKSTART.md to get started")
    print("  Check docs/ for detailed guides")
    print("  Run examples/ to see capabilities\n")

if __name__ == "__main__":
    main()
