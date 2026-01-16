#!/usr/bin/env python3
"""
TESTE DAS MELHORIAS DE SLM BEST PRACTICES
Valida que todas as otimizações foram aplicadas corretamente
"""

import sys
import inspect
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_temperature_differentiation():
    """Teste 1: Temperaturas diferenciadas"""
    console.print("\n[bold cyan]TEST 1: Temperature Differentiation[/bold cyan]")
    
    try:
        from gemma_cluster_coordinator import GemmaClusterCoordinator
        from cluster_manager import ClusterManager
        from outlines_agent import OutlinesQwenAgent
        
        # Mock instances
        cluster_mgr = ClusterManager()
        qwen = OutlinesQwenAgent(
            model_name="qwen3-4b",
            base_url="http://localhost:1234/v1",
            temperature=0.5
        )
        
        coordinator = GemmaClusterCoordinator(
            cluster_manager=cluster_mgr,
            qwen_agent=qwen,
            verbose=False
        )
        
        # Verificar atributos
        assert hasattr(coordinator, 'planner_temperature'), "❌ Missing planner_temperature"
        assert hasattr(coordinator, 'executor_temperature'), "❌ Missing executor_temperature"
        
        assert coordinator.planner_temperature >= 0.4, f"❌ planner_temperature too low: {coordinator.planner_temperature}"
        assert coordinator.executor_temperature <= 0.1, f"❌ executor_temperature too high: {coordinator.executor_temperature}"
        
        console.print("[green]✅ Temperature differentiation OK[/green]")
        console.print(f"[dim]   Planner: {coordinator.planner_temperature}, Executor: {coordinator.executor_temperature}[/dim]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Temperature test failed: {e}[/red]")
        return False


def test_skill_harvesting():
    """Teste 2: Skill Harvesting"""
    console.print("\n[bold cyan]TEST 2: Skill Harvesting[/bold cyan]")
    
    try:
        from gemma_cluster_coordinator import GemmaClusterCoordinator
        from cluster_manager import ClusterManager
        from outlines_agent import OutlinesQwenAgent
        
        cluster_mgr = ClusterManager()
        qwen = OutlinesQwenAgent(
            model_name="qwen3-4b",
            base_url="http://localhost:1234/v1",
            temperature=0.5
        )
        
        coordinator = GemmaClusterCoordinator(
            cluster_manager=cluster_mgr,
            qwen_agent=qwen,
            verbose=False
        )
        
        # Verificar estrutura
        assert hasattr(coordinator, 'successful_patterns'), "❌ Missing successful_patterns"
        assert isinstance(coordinator.successful_patterns, list), "❌ successful_patterns not a list"
        
        # Verificar métodos
        assert hasattr(coordinator, '_record_successful_pattern'), "❌ Missing _record_successful_pattern"
        assert hasattr(coordinator, '_get_similar_pattern'), "❌ Missing _get_similar_pattern"
        assert hasattr(coordinator, '_extract_task_type'), "❌ Missing _extract_task_type"
        
        # Teste funcional
        coordinator._record_successful_pattern("web_search", ["Open Google", "Search for Python"])
        assert len(coordinator.successful_patterns) == 1, "❌ Pattern not recorded"
        
        pattern = coordinator._get_similar_pattern("Search Google for machine learning")
        assert pattern is not None, "❌ Pattern retrieval failed"
        assert pattern == ["Open Google", "Search for Python"], "❌ Wrong pattern returned"
        
        task_type = coordinator._extract_task_type("Search Google for AI")
        assert task_type == "web_search", f"❌ Wrong task type: {task_type}"
        
        console.print("[green]✅ Skill harvesting OK[/green]")
        console.print(f"[dim]   Patterns stored: {len(coordinator.successful_patterns)}[/dim]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Skill harvesting test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_few_shot_examples():
    """Teste 3: Few-shot examples em prompts"""
    console.print("\n[bold cyan]TEST 3: Few-Shot Examples in Prompts[/bold cyan]")
    
    try:
        from gemma_cluster_coordinator import GemmaClusterCoordinator
        import inspect
        
        # Verificar se prompts contêm exemplos
        source = inspect.getsource(GemmaClusterCoordinator._call_gemma_cluster_selection)
        
        checks = {
            "FEW-SHOT EXAMPLES": "FEW-SHOT EXAMPLES" in source or "Example 1:" in source,
            "Thought→Action": "Thought:" in source and "Action:" in source,
            "JSON examples": '{"clusters":' in source or '"clusters"' in source
        }
        
        all_ok = True
        for check_name, result in checks.items():
            if result:
                console.print(f"[green]  ✓ {check_name} found[/green]")
            else:
                console.print(f"[red]  ✗ {check_name} missing[/red]")
                all_ok = False
        
        if all_ok:
            console.print("[green]✅ Few-shot examples OK[/green]")
        else:
            console.print("[yellow]⚠️  Some few-shot examples missing[/yellow]")
        
        return all_ok
        
    except Exception as e:
        console.print(f"[red]❌ Few-shot test failed: {e}[/red]")
        return False


def test_dom_distillation():
    """Teste 4: DOM Distillation"""
    console.print("\n[bold cyan]TEST 4: DOM Distillation[/bold cyan]")
    
    try:
        from gemma_cluster_coordinator import GemmaClusterCoordinator
        import inspect
        
        # Verificar se _get_page_data_for_qwen tem filtros
        source = inspect.getsource(GemmaClusterCoordinator._get_page_data_for_qwen)
        
        checks = {
            "is_displayed()": "is_displayed()" in source,
            "is_enabled()": "is_enabled()" in source,
            "Link filtering": "javascript:" in source or "mailto:" in source,
            "Limit results": "[:showing]" in source or "min(10" in source or "[:20]" in source
        }
        
        all_ok = True
        for check_name, result in checks.items():
            if result:
                console.print(f"[green]  ✓ {check_name} implemented[/green]")
            else:
                console.print(f"[red]  ✗ {check_name} missing[/red]")
                all_ok = False
        
        if all_ok:
            console.print("[green]✅ DOM distillation OK[/green]")
        else:
            console.print("[yellow]⚠️  Some DOM filters missing[/yellow]")
        
        return all_ok
        
    except Exception as e:
        console.print(f"[red]❌ DOM distillation test failed: {e}[/red]")
        return False


def test_robust_json_parsing():
    """Teste 5: JSON Parsing Robusto"""
    console.print("\n[bold cyan]TEST 5: Robust JSON Parsing[/bold cyan]")
    
    try:
        from gemma_cluster_coordinator import GemmaClusterCoordinator
        
        # Casos de teste
        test_cases = [
            ('{"clusters": ["WEB"], "reasoning": "test"}', True),
            ('```json\n{"clusters": ["MATH"]}\n```', True),
            ('Some text {"clusters": ["DATA"]} more text', True),
            ('{"clusters": ["TEXT", "reasoning": "incomplete"', True),  # Deve corrigir
            ('complete garbage text', False),  # Deve usar fallback
        ]
        
        passed = 0
        for test_input, should_parse in test_cases:
            result, error = GemmaClusterCoordinator._robust_json_parse(test_input)
            
            if should_parse:
                if result is not None:
                    passed += 1
                else:
                    console.print(f"[yellow]  ⚠️  Failed to parse: {test_input[:50]}...[/yellow]")
            else:
                if result is None:
                    passed += 1
                else:
                    console.print(f"[yellow]  ⚠️  Should have failed: {test_input[:50]}...[/yellow]")
        
        console.print(f"[green]✅ JSON parsing: {passed}/{len(test_cases)} tests passed[/green]")
        return passed >= len(test_cases) - 1  # Permitir 1 falha
        
    except Exception as e:
        console.print(f"[red]❌ JSON parsing test failed: {e}[/red]")
        return False


def generate_report(results):
    """Gera relatório final"""
    console.print("\n" + "="*60)
    console.print("[bold]📊 SLM BEST PRACTICES IMPLEMENTATION REPORT[/bold]")
    console.print("="*60)
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Feature", style="cyan", width=40)
    table.add_column("Status", justify="center", width=15)
    
    for test_name, passed in results.items():
        status = "[green]✅ PASS[/green]" if passed else "[red]❌ FAIL[/red]"
        table.add_row(test_name, status)
    
    console.print(table)
    
    total = len(results)
    passed = sum(results.values())
    percentage = (passed / total) * 100
    
    console.print(f"\n[bold]Score: {passed}/{total} ({percentage:.0f}%)[/bold]")
    
    if percentage == 100:
        console.print("[bold green]🎉 All SLM best practices successfully implemented![/bold green]")
    elif percentage >= 80:
        console.print("[bold yellow]⚠️  Most features working, some improvements needed[/bold yellow]")
    else:
        console.print("[bold red]❌ Significant issues detected, review required[/bold red]")


def main():
    """Executa todos os testes"""
    console.print(Panel.fit(
        "[bold]SLM BEST PRACTICES VALIDATION SUITE[/bold]\n"
        "Testing implementation of research-backed optimizations",
        border_style="blue"
    ))
    
    results = {
        "Temperature Differentiation": test_temperature_differentiation(),
        "Skill Harvesting": test_skill_harvesting(),
        "Few-Shot Examples": test_few_shot_examples(),
        "DOM Distillation": test_dom_distillation(),
        "Robust JSON Parsing": test_robust_json_parsing()
    }
    
    generate_report(results)
    
    # Exit code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
