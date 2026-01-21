#!/usr/bin/env python3
"""
TESTE DAS CORREÇÕES
Valida que matemática não abre Google
"""

from cluster_manager import create_default_cluster_manager
from outlines_agent import OutlinesQwenAgent
from gemma_cluster_coordinator import GemmaClusterCoordinator

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
    verbose=True
)

# TEST: Matemática simples (NÃO deve abrir Google)
print('='*80)
print('🧪 TESTE: Calcule 15 ao quadrado')
print('='*80)
result = coordinator.query_step_by_step('Calcule 15 ao quadrado')
print('\n' + '='*80)
print('✅ RESULTADO:', result)
print('='*80)
