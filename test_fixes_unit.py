#!/usr/bin/env python3
"""
TESTE FOCADO: Verifica se TODO list evita web para matemática
"""

from cluster_manager import ClusterManager, create_default_cluster_manager
from outlines_agent import OutlinesQwenAgent
from gemma_cluster_coordinator import GemmaClusterCoordinator
from rich.console import Console

console = Console()

# Setup
cm = create_default_cluster_manager()
qwen = OutlinesQwenAgent(
    model_name='qwen3-4b-toolcalling-codex',
    base_url='http://localhost:1234/v1',
    temperature=0.1,
    verbose=False
)

coordinator = GemmaClusterCoordinator(
    cluster_manager=cm,
    qwen_agent=qwen,
    gemma_model='google/gemma-3-4b',
    max_iterations=5,
    verbose=False  # Silenciar para focar no resultado
)

print('='*80)
print('🧪 TESTE: Verificação de TODO list para "Calcule 15 ao quadrado"')
print('='*80)

# Criar TODO list
todo_data = coordinator._gemma_create_todo('Calcule 15 ao quadrado')

print('\n📋 TODO CRIADO:')
print(f"   Main Goal: {todo_data.get('main_goal', 'N/A')}")
print(f"   Número de tasks: {len(todo_data.get('tasks', []))}")
print()

# Verificar tasks
tasks_ok = True
for i, task in enumerate(todo_data.get('tasks', []), 1):
    desc = task.get('description', '')
    desc_lower = desc.lower()
    
    # Verificar se menciona navegação/web incorretamente
    bad_keywords = ['google', 'search', 'browser', 'navigate', 'web', 'url', 'pesquis', 'naveg', 'abrir']
    has_bad = any(kw in desc_lower for kw in bad_keywords)
    
    status = '✅' if not has_bad else '❌'
    print(f'{status} Task {i}: {desc}')
    
    if has_bad:
        tasks_ok = False
        found_bad = [kw for kw in bad_keywords if kw in desc_lower]
        print(f'   ⚠️  Contém keywords de web: {found_bad}')

print()
print('='*80)

# Teste de cluster selection
print('\n🗂️  TESTE: Seleção de clusters')
cluster_suggestions = cm.suggest_clusters_for_task('Calcule 15 ao quadrado')
print(f'   Sugestões do ClusterManager: {cluster_suggestions}')

# Verificar se MATH está incluído
if 'MATH' in cluster_suggestions:
    print('   ✅ MATH detectado corretamente')
else:
    print('   ❌ MATH NÃO detectado')

if 'WEB' in cluster_suggestions:
    print('   ❌ WEB detectado incorretamente')
else:
    print('   ✅ WEB não detectado (correto)')

print()
print('='*80)

# Teste de subtasks
print('\n📝 TESTE: Criação de subtasks para "Compute 15 * 15"')
subtasks = coordinator._gemma_create_subtasks('Compute 15 * 15')

print(f'   Número de subtasks: {len(subtasks)}')
print()

subtasks_ok = True
for i, subtask in enumerate(subtasks, 1):
    sub_lower = subtask.lower()
    
    # Verificar se primeira subtask tenta abrir Google
    is_first = (i == 1)
    opens_google = 'google.com' in sub_lower or ('open' in sub_lower and 'url' in sub_lower)
    
    if is_first and opens_google:
        print(f'❌ Subtask {i}: {subtask}')
        print(f'   ⚠️  PRIMEIRA subtask abre Google (BUG!)')
        subtasks_ok = False
    else:
        status = '✅'
        print(f'{status} Subtask {i}: {subtask}')

print()
print('='*80)

# Sumário
print('\n📊 SUMÁRIO DOS TESTES:')
print(f'   ✅ TODO list sem web keywords: {tasks_ok}')
print(f'   ✅ ClusterManager detecta MATH: {"MATH" in cluster_suggestions}')
print(f'   ✅ ClusterManager não detecta WEB: {"WEB" not in cluster_suggestions}')
print(f'   ✅ Subtasks não abrem Google: {subtasks_ok}')

all_passed = tasks_ok and 'MATH' in cluster_suggestions and 'WEB' not in cluster_suggestions and subtasks_ok

if all_passed:
    print('\n🎉 TODOS OS TESTES PASSARAM!')
else:
    print('\n⚠️  ALGUNS TESTES FALHARAM')

print('='*80)
