#!/usr/bin/env python3
"""
TESTE PRÁTICO DE USO - Mini Agent
Demonstra casos de uso reais do sistema hierárquico Gemma+Qwen
"""

import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from cluster_manager import create_default_cluster_manager
from outlines_agent import OutlinesQwenAgent
from gemma_cluster_coordinator import GemmaClusterCoordinator

console = Console()


class PracticalTest:
    """Testes práticos do Mini Agent"""
    
    def __init__(self):
        """Inicializa o coordenador"""
        console.print("\n[bold cyan]🚀 Inicializando Mini Agent...[/bold cyan]")
        
        # Setup
        self.cluster_manager = create_default_cluster_manager()
        self.qwen_agent = OutlinesQwenAgent(
            model_name="qwen3-4b-toolcalling-codex",
            base_url="http://localhost:1234/v1",
            temperature=0.2,
            verbose=False
        )
        
        self.coordinator = GemmaClusterCoordinator(
            cluster_manager=self.cluster_manager,
            qwen_agent=self.qwen_agent,
            gemma_model="google/gemma-3-4b",
            max_iterations=10,
            verbose=True
        )
        
        console.print("[green]✓ Sistema iniciado com sucesso![/green]\n")
        
        self.results = []
    
    def run_test(self, test_name: str, query: str, expected_outcome: str):
        """
        Executa um teste prático
        
        Args:
            test_name: Nome do teste
            query: Query para o agente
            expected_outcome: Resultado esperado
        """
        console.print("="*80)
        console.print(f"[bold magenta]TEST: {test_name}[/bold magenta]")
        console.print("="*80)
        console.print(f"[cyan]Query:[/cyan] {query}")
        console.print(f"[dim]Expected:[/dim] {expected_outcome}\n")
        
        start_time = time.time()
        
        try:
            result = self.coordinator.query_step_by_step(query)
            duration = time.time() - start_time
            
            console.print("\n" + "="*80)
            console.print(f"[bold green]✓ RESULTADO:[/bold green]")
            console.print(Panel(result, border_style="green"))
            console.print(f"[dim]Tempo: {duration:.2f}s | Iterações: {len(self.coordinator.conversation_history)}[/dim]")
            
            self.results.append({
                "test": test_name,
                "success": True,
                "duration": duration,
                "iterations": len(self.coordinator.conversation_history),
                "result_preview": result[:100] + "..." if len(result) > 100 else result
            })
            
        except Exception as e:
            duration = time.time() - start_time
            console.print(f"\n[red]✗ ERRO:[/red] {str(e)}")
            
            self.results.append({
                "test": test_name,
                "success": False,
                "duration": duration,
                "iterations": 0,
                "error": str(e)
            })
        
        console.print("\n")
    
    def print_summary(self):
        """Imprime sumário dos resultados"""
        console.print("\n" + "="*80)
        console.print("[bold]📊 SUMÁRIO DOS TESTES PRÁTICOS[/bold]")
        console.print("="*80 + "\n")
        
        table = Table(title="Resultados", box=box.ROUNDED)
        table.add_column("Teste", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Tempo", justify="right")
        table.add_column("Iterações", justify="center")
        
        total_success = 0
        total_time = 0.0
        
        for result in self.results:
            status = "[green]✓ OK[/green]" if result["success"] else "[red]✗ FALHA[/red]"
            duration = f"{result['duration']:.2f}s"
            iterations = str(result["iterations"])
            
            table.add_row(
                result["test"],
                status,
                duration,
                iterations
            )
            
            if result["success"]:
                total_success += 1
            total_time += result["duration"]
        
        console.print(table)
        
        console.print(f"\n[bold]Estatísticas:[/bold]")
        console.print(f"  • Testes executados: {len(self.results)}")
        console.print(f"  • Sucessos: {total_success}/{len(self.results)} ({100*total_success/len(self.results):.0f}%)")
        console.print(f"  • Tempo total: {total_time:.2f}s")
        console.print(f"  • Tempo médio: {total_time/len(self.results):.2f}s/teste")
        
        if total_success == len(self.results):
            console.print("\n[bold green]🎉 TODOS OS TESTES PASSARAM![/bold green]")
        else:
            console.print(f"\n[bold yellow]⚠️  {len(self.results) - total_success} teste(s) falharam[/bold yellow]")


def main():
    """Executa testes práticos"""
    console.print(Panel.fit(
        "[bold]MINI AGENT - TESTES PRÁTICOS DE USO[/bold]\n\n"
        "[yellow]Sistema Hierárquico: Gemma-3-4B (planejador) + Qwen-3-4B (executor)[/yellow]\n"
        "[dim]Demonstração de casos de uso reais[/dim]",
        border_style="blue"
    ))
    
    try:
        tester = PracticalTest()
    except Exception as e:
        console.print(f"\n[red]❌ Erro ao inicializar:[/red] {e}")
        console.print("\n[yellow]Verifique:[/yellow]")
        console.print("  1. LM Studio está rodando (http://localhost:1234)")
        console.print("  2. Modelos Gemma-3-4B e Qwen-3-4B carregados")
        console.print("  3. Execute: python validate_setup.py")
        return 1
    
    # =========================================================================
    # TESTE 1: Cálculo matemático simples
    # =========================================================================
    tester.run_test(
        test_name="Cálculo Matemático",
        query="Calcule 15 ao quadrado",
        expected_outcome="225"
    )
    
    # =========================================================================
    # TESTE 2: Conversão de moeda
    # =========================================================================
    tester.run_test(
        test_name="Conversão de Moeda",
        query="Converta 100 dólares para euros",
        expected_outcome="~85-95 EUR (depende da taxa)"
    )
    
    # =========================================================================
    # TESTE 3: Análise de texto
    # =========================================================================
    tester.run_test(
        test_name="Análise de Texto",
        query="Analise o texto: 'Python é uma linguagem de programação versátil e poderosa'",
        expected_outcome="Estatísticas do texto (palavras, caracteres, etc)"
    )
    
    # =========================================================================
    # TESTE 4: Data e hora
    # =========================================================================
    tester.run_test(
        test_name="Data e Hora Atual",
        query="Que dia é hoje?",
        expected_outcome="Data atual do sistema"
    )
    
    # =========================================================================
    # TESTE 5: Cálculo combinado (múltiplas operações)
    # =========================================================================
    tester.run_test(
        test_name="Cálculos Combinados",
        query="Calcule (25 + 15) multiplicado por 3, depois divida por 2",
        expected_outcome="60"
    )
    
    # =========================================================================
    # TESTE 6: Navegação web (caso browser disponível)
    # =========================================================================
    console.print("[dim]Pulando teste de navegação web (requer browser configurado)[/dim]\n")
    
    # Sumário
    tester.print_summary()
    
    return 0 if all(r["success"] for r in tester.results) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Teste interrompido pelo usuário[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]❌ Erro fatal:[/red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
