#!/usr/bin/env python3
"""
Setup validation script - Checks if all dependencies are installed.
Run this before using the agent system.
"""

import sys
import importlib.util
from typing import List, Tuple

# Lista de dependências críticas
REQUIRED_PACKAGES = [
    ("openai", "openai>=1.12.0"),
    ("dotenv", "python-dotenv>=1.0.0"),
    ("requests", "requests>=2.31.0"),
    ("pydantic", "pydantic>=2.5.0"),
    ("rich", "rich>=13.7.0"),
    ("selenium", "selenium>=4.15.0"),
]

OPTIONAL_PACKAGES = [
    ("webdriver_manager", "webdriver-manager>=4.0.0"),
]


def check_package(package_name: str, pip_name: str) -> Tuple[bool, str]:
    """
    Verifica se um pacote está instalado.
    
    Args:
        package_name: Nome do módulo para importar
        pip_name: Nome do pacote no pip
        
    Returns:
        Tupla (instalado: bool, versão ou erro: str)
    """
    spec = importlib.util.find_spec(package_name)
    
    if spec is None:
        return False, f"NOT FOUND - Install with: pip install {pip_name}"
    
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, "__version__", "unknown")
        return True, f"✓ Installed (version: {version})"
    except Exception as e:
        return False, f"ERROR - {str(e)}"


def check_lm_studio_connection():
    """Verifica se o LM Studio está acessível."""
    try:
        import requests
        response = requests.get("http://localhost:1234/v1/models", timeout=3)
        if response.status_code == 200:
            models = response.json()
            return True, f"✓ Connected - {len(models.get('data', []))} models loaded"
        else:
            return False, f"Connection failed (status: {response.status_code})"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect - Make sure LM Studio is running"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main validation."""
    print("="*60)
    print("MINI AGENT - SETUP VALIDATION")
    print("="*60)
    print()
    
    all_ok = True
    
    # Check required packages
    print("📦 REQUIRED PACKAGES:")
    print("-"*60)
    
    for package, pip_name in REQUIRED_PACKAGES:
        installed, message = check_package(package, pip_name)
        status = "✓" if installed else "✗"
        print(f"  {status} {package:20s} {message}")
        if not installed:
            all_ok = False
    
    print()
    
    # Check optional packages
    print("📦 OPTIONAL PACKAGES:")
    print("-"*60)
    
    for package, pip_name in OPTIONAL_PACKAGES:
        installed, message = check_package(package, pip_name)
        status = "✓" if installed else "○"
        print(f"  {status} {package:20s} {message}")
    
    print()
    
    # Check LM Studio
    print("🌐 LM STUDIO CONNECTION:")
    print("-"*60)
    
    connected, message = check_lm_studio_connection()
    status = "✓" if connected else "✗"
    print(f"  {status} LM Studio (localhost:1234) {message}")
    
    if not connected:
        print()
        print("  💡 TIP: Start LM Studio and load a model before running the agent")
    
    print()
    print("="*60)
    
    if all_ok:
        print("✅ SETUP VALIDATION PASSED")
        print()
        print("You're ready to use Mini Agent!")
        print("Run: python main.py")
        return 0
    else:
        print("❌ SETUP VALIDATION FAILED")
        print()
        print("Install missing packages:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
