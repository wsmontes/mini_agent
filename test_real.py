#!/usr/bin/env python3
"""
TESTE REAL - Executa query completa e valida resultado
"""

from cluster_manager import create_default_cluster_manager
from tools.calculator import CalculatorTool

print('='*80)
print('🧪 TESTE REAL: Calculator tool direto')
print('='*80)

# Teste 1: Tool funciona?
calc = CalculatorTool()
result = calc.execute('15 * 15')

print(f'\n📊 Resultado do calculator:')
print(f'   Input: "15 * 15"')
print(f'   Output: {result}')

expected = 225
actual = result.get('result', None)

if actual == expected:
    print(f'   ✅ CORRETO: {actual} == {expected}')
else:
    print(f'   ❌ ERRADO: {actual} != {expected}')

print()
print('='*80)
print('🧪 TESTE REAL: Query completa sem Gemma (Qwen direto)')
print('='*80)

from outlines_agent import OutlinesQwenAgent

cm = create_default_cluster_manager()
tools_list = cm.get_tools_by_clusters(['MATH'])
tools_dict = {tool.name: tool for tool in tools_list}

qwen = OutlinesQwenAgent(
    model_name='qwen3-4b-toolcalling-codex',
    base_url='http://localhost:1234/v1',
    temperature=0.1,
    verbose=True
)

# Registrar tools
for tool in tools_list:
    qwen.register_tool(tool)

print('\n🤖 Qwen query: "Calculate 15 squared. Use the calculator tool with expression 15*15"')
response = qwen.query(
    'Calculate 15 squared. Use the calculator tool with expression "15*15". Return only the numeric result.',
    max_tool_iterations=3
)

print(f'\n📊 Resposta do Qwen:')
print(f'   {response}')

# Verificar se contém 225
if '225' in str(response):
    print(f'   ✅ Contém 225')
else:
    print(f'   ❌ Não contém 225')

print()
print('='*80)
