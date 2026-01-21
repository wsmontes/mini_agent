#!/usr/bin/env python3
"""
TESTE MÍNIMO - Só calculator, prompt explícito
"""

from outlines_agent import OutlinesQwenAgent
from tools.calculator import CalculatorTool

print('='*80)
print('🧪 TESTE MÍNIMO: Qwen + 1 tool + prompt explícito')
print('='*80)

qwen = OutlinesQwenAgent(
    model_name='qwen3-4b-toolcalling-codex',
    base_url='http://localhost:1234/v1',
    temperature=0.0,  # Determinístico
    verbose=True
)

# Só calculator
calc = CalculatorTool()
qwen.register_tool(calc)

# Prompt BEM explícito
qwen.reset_conversation()
response = qwen.query(
    'Use the calculator tool ONCE with expression "15*15". After getting the result, respond with ONLY the number.',
    max_tool_iterations=2  # Máximo 2 iterações
)

print(f'\n📊 RESPOSTA:')
print(f'   {response}')
print()

if '225' in str(response):
    print('   ✅ Sucesso!')
else:
    print('   ❌ Falhou')

print('='*80)
