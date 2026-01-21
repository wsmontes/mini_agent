#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO - Entender o comportamento real do sistema
"""

from outlines_agent import OutlinesQwenAgent
from tools.calculator import CalculatorTool
import json

print('='*80)
print('🔬 DIAGNÓSTICO COMPLETO DO SISTEMA')
print('='*80)

qwen = OutlinesQwenAgent(
    model_name='qwen3-4b-toolcalling-codex',
    base_url='http://localhost:1234/v1',
    temperature=0.0,
    verbose=False  # Vamos adicionar nosso próprio logging
)

calc = CalculatorTool()
qwen.register_tool(calc)

print('\n📋 ESTADO INICIAL:')
print(f'   Tools registradas: {list(qwen.tools.keys())}')
print(f'   Tool schemas: {len(qwen.tool_schemas)}')

# Fazer query manualmente com logging detalhado
qwen.messages.append({"role": "user", "content": "Calculate 15*15 using the calculator tool."})

print('\n' + '='*80)
print('ITERAÇÃO 1')
print('='*80)

# Call API
response = qwen.client.chat.completions.create(
    model=qwen.model_name,
    messages=qwen.messages,
    temperature=0.0,
    tools=qwen.tool_schemas,
    max_tokens=500
)

choice = response.choices[0]
msg = choice.message

print(f'\n📥 RESPOSTA DO LM STUDIO:')
print(f'   finish_reason: {choice.finish_reason}')
print(f'   message.content: {repr(msg.content)}')
print(f'   message.tool_calls: {msg.tool_calls}')

if msg.content:
    print(f'\n📄 CONTENT (primeiros 500 chars):')
    print(f'   {msg.content[:500]}')
    
    # Tentar parsear JSON
    content_clean = msg.content.strip().replace("<end_of_turn>", "").strip()
    if content_clean.startswith("["):
        try:
            parsed = json.loads(content_clean)
            print(f'\n✅ Content é JSON válido: {type(parsed)}')
            if isinstance(parsed, list):
                print(f'   Número de tool calls: {len(parsed)}')
                for i, tc in enumerate(parsed, 1):
                    print(f'   Tool {i}: {tc.get("name")} com args: {tc.get("arguments")}')
        except json.JSONDecodeError as e:
            print(f'\n❌ Content não é JSON válido: {e}')

# Executar tool call se existir
if msg.content and msg.content.strip().startswith("["):
    try:
        tool_calls_json = json.loads(msg.content.strip().replace("<end_of_turn>", "").strip())
        if isinstance(tool_calls_json, list) and len(tool_calls_json) > 0:
            tc = tool_calls_json[0]
            print(f'\n🔧 EXECUTANDO TOOL: {tc["name"]}')
            result = calc.execute(**tc["arguments"])
            print(f'   Resultado: {result}')
            
            # Adicionar ao histórico como LM Studio espera
            qwen.messages.append({
                "role": "assistant",
                "content": msg.content
            })
            qwen.messages.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": f"call_{tc['name']}_1"
            })
            
            print(f'\n📋 HISTÓRICO APÓS TOOL CALL:')
            for i, m in enumerate(qwen.messages):
                role = m.get('role')
                content_preview = str(m.get('content', ''))[:100]
                print(f'   {i+1}. {role}: {content_preview}...')
            
            # Segunda iteração
            print('\n' + '='*80)
            print('ITERAÇÃO 2')
            print('='*80)
            
            response2 = qwen.client.chat.completions.create(
                model=qwen.model_name,
                messages=qwen.messages,
                temperature=0.0,
                tools=qwen.tool_schemas,
                max_tokens=500
            )
            
            choice2 = response2.choices[0]
            msg2 = choice2.message
            
            print(f'\n📥 RESPOSTA DO LM STUDIO (após tool result):')
            print(f'   finish_reason: {choice2.finish_reason}')
            print(f'   message.content: {repr(msg2.content)}')
            print(f'   message.tool_calls: {msg2.tool_calls}')
            
            if msg2.content:
                print(f'\n📄 CONTENT (primeiros 500 chars):')
                print(f'   {msg2.content[:500]}')
                
                # Verificar se é texto ou tool call repetido
                content_clean2 = msg2.content.strip().replace("<end_of_turn>", "").strip()
                if content_clean2.startswith("["):
                    print(f'\n⚠️  PROBLEMA: Modelo retornou TOOL CALL novamente ao invés de texto!')
                    try:
                        parsed2 = json.loads(content_clean2)
                        print(f'   Tool calls repetidos: {parsed2}')
                    except:
                        pass
                else:
                    print(f'\n✅ Modelo retornou TEXTO (não tool call)')
                    if '225' in content_clean2:
                        print(f'   ✅ Resposta contém 225!')

    except Exception as e:
        print(f'\n❌ Erro ao processar: {e}')
        import traceback
        traceback.print_exc()

print('\n' + '='*80)
print('FIM DO DIAGNÓSTICO')
print('='*80)
