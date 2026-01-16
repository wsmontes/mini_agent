#!/usr/bin/env python3
"""
CLUSTER MANAGER
Organiza tools em clusters temáticos e permite seleção inteligente
"""

from typing import Dict, List, Set
from tools.base import BaseTool


class ClusterManager:
    """
    Gerencia clusters de ferramentas por domínio/natureza
    
    Baseado em análise empírica com Gemma sobre 36 tarefas diversas:
    - 75% de consistência na classificação
    - 25 clusters identificados naturalmente
    - Consolidados em 7 super-clusters principais
    """
    
    # Definição dos super-clusters baseada nos resultados empíricos
    CLUSTER_DEFINITIONS = {
        "MATH": {
            "description": "Mathematical operations, calculations, statistics",
            "keywords": ["calculate", "math", "number", "equation", "compute", "sum", "average", "statistics"],
            "sub_clusters": ["mathematics", "math", "math/finance"]
        },
        "WEB": {
            "description": "Web browsing, navigation, clicking, form filling",
            "keywords": ["web", "browser", "click", "navigate", "url", "page", "link", "website"],
            "sub_clusters": ["web retrieval", "browser interaction", "web search", "browser", "web form", "web input"]
        },
        "DATA": {
            "description": "File operations, data analysis, CSV/JSON processing",
            "keywords": ["file", "data", "csv", "json", "read", "write", "analyze", "process", "parse"],
            "sub_clusters": ["data processing", "data analysis", "file processing", "filesystem", "data visualization"]
        },
        "TEXT": {
            "description": "Text processing, NLP, translation, summarization",
            "keywords": ["text", "translate", "summarize", "language", "words", "paragraph", "document"],
            "sub_clusters": ["text processing", "text summarization", "language translation", "text generation", "text analysis"]
        },
        "COMMUNICATION": {
            "description": "Email, messaging, notifications, API calls",
            "keywords": ["email", "send", "message", "notify", "api", "request", "post", "fetch"],
            "sub_clusters": ["communication", "web api", "web data retrieval"]
        },
        "SYSTEM": {
            "description": "System operations, file system, commands, datetime",
            "keywords": ["system", "command", "execute", "datetime", "time", "date", "directory", "path"],
            "sub_clusters": ["system", "filesystem"]
        },
        "CODE": {
            "description": "Programming, code generation, debugging",
            "keywords": ["code", "programming", "function", "python", "script", "debug", "compile"],
            "sub_clusters": ["programming", "security"]
        }
    }
    
    def __init__(self):
        """Inicializa o gerenciador de clusters"""
        self.clusters: Dict[str, List[BaseTool]] = {
            cluster: [] for cluster in self.CLUSTER_DEFINITIONS.keys()
        }
        self.tool_to_clusters: Dict[str, Set[str]] = {}  # Mapeia tool -> seus clusters
    
    def register_tool(self, tool: BaseTool, clusters: List[str]):
        """
        Registra uma tool em um ou mais clusters
        
        Args:
            tool: Instância da ferramenta
            clusters: Lista de nomes de clusters onde a tool pertence
        """
        tool_name = tool.name
        
        for cluster_name in clusters:
            if cluster_name not in self.clusters:
                raise ValueError(f"Cluster '{cluster_name}' não existe. Clusters válidos: {list(self.clusters.keys())}")
            
            self.clusters[cluster_name].append(tool)
            
            if tool_name not in self.tool_to_clusters:
                self.tool_to_clusters[tool_name] = set()
            self.tool_to_clusters[tool_name].add(cluster_name)
    
    def get_tools_by_clusters(self, cluster_names: List[str]) -> List[BaseTool]:
        """
        Retorna todas as tools de um ou mais clusters (sem duplicatas)
        
        Args:
            cluster_names: Lista de nomes de clusters
            
        Returns:
            Lista única de ferramentas dos clusters solicitados
        """
        tools_set = set()
        tools_list = []
        
        for cluster_name in cluster_names:
            if cluster_name not in self.clusters:
                continue
                
            for tool in self.clusters[cluster_name]:
                if tool.name not in tools_set:
                    tools_set.add(tool.name)
                    tools_list.append(tool)
        
        return tools_list
    
    def get_all_clusters_info(self) -> Dict[str, Dict]:
        """
        Retorna informações sobre todos os clusters
        
        Returns:
            Dict com nome do cluster -> {description, tool_count, tools}
        """
        info = {}
        
        for cluster_name, tools in self.clusters.items():
            info[cluster_name] = {
                "description": self.CLUSTER_DEFINITIONS[cluster_name]["description"],
                "tool_count": len(tools),
                "tools": [tool.name for tool in tools],
                "keywords": self.CLUSTER_DEFINITIONS[cluster_name]["keywords"]
            }
        
        return info
    
    def suggest_clusters_for_task(self, task_description: str) -> List[str]:
        """
        Sugere clusters baseado em keywords na descrição da tarefa
        (Fallback simples caso o Gemma não esteja disponível)
        
        Args:
            task_description: Descrição da tarefa em linguagem natural
            
        Returns:
            Lista de clusters sugeridos (ordenados por relevância)
        """
        task_lower = task_description.lower()
        cluster_scores = {}
        
        for cluster_name, definition in self.CLUSTER_DEFINITIONS.items():
            score = 0
            for keyword in definition["keywords"]:
                if keyword in task_lower:
                    score += 1
            
            if score > 0:
                cluster_scores[cluster_name] = score
        
        # Retorna clusters ordenados por score (do maior para o menor)
        sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1], reverse=True)
        return [cluster for cluster, score in sorted_clusters]
    
    def get_cluster_stats(self) -> Dict[str, int]:
        """Retorna estatísticas sobre os clusters"""
        return {
            cluster: len(tools) 
            for cluster, tools in self.clusters.items()
        }
    
    @staticmethod
    def get_cluster_names() -> List[str]:
        """Retorna lista de nomes de clusters disponíveis"""
        return list(ClusterManager.CLUSTER_DEFINITIONS.keys())
    
    @staticmethod
    def get_cluster_description(cluster_name: str) -> str:
        """Retorna descrição de um cluster específico"""
        if cluster_name in ClusterManager.CLUSTER_DEFINITIONS:
            return ClusterManager.CLUSTER_DEFINITIONS[cluster_name]["description"]
        return ""


def create_default_cluster_manager():
    """
    Cria um ClusterManager com as tools padrão já registradas
    
    Returns:
        ClusterManager configurado
    """
    from tools.calculator import CalculatorTool
    from tools.general_tools import (
        AdvancedCalculatorTool, DateTimeTool, TextAnalysisTool,
        CurrencyConverterTool
    )
    from tools.browser_tools import (
        OpenURLTool, GetPageContentTool, ClickElementTool,
        FillFormTool, TakeScreenshotTool, ScrollPageTool,
        FindElementsTool, CloseBrowserTool
    )
    from tools.extract_links_tool import ExtractLinksTool
    from tools.click_link_by_index_tool import ClickLinkByIndexTool
    
    manager = ClusterManager()
    
    # MATH cluster
    manager.register_tool(CalculatorTool(), ["MATH"])
    manager.register_tool(AdvancedCalculatorTool(), ["MATH"])
    manager.register_tool(CurrencyConverterTool(), ["MATH"])
    
    # WEB cluster
    manager.register_tool(OpenURLTool(), ["WEB"])
    manager.register_tool(GetPageContentTool(), ["WEB"])
    manager.register_tool(ClickElementTool(), ["WEB"])
    manager.register_tool(FillFormTool(), ["WEB"])
    manager.register_tool(ScrollPageTool(), ["WEB"])
    manager.register_tool(FindElementsTool(), ["WEB"])
    manager.register_tool(ExtractLinksTool(), ["WEB"])  # Nova tool
    manager.register_tool(ClickLinkByIndexTool(), ["WEB"])  # Nova tool
    manager.register_tool(CloseBrowserTool(), ["WEB"])
    
    # DATA cluster
    # (Adicionar quando tivermos tools de CSV/JSON)
    
    # TEXT cluster
    manager.register_tool(TextAnalysisTool(), ["TEXT"])
    
    # SYSTEM cluster
    manager.register_tool(DateTimeTool(), ["SYSTEM"])
    
    # COMMUNICATION cluster
    # (Adicionar quando tivermos tools de email/API)
    
    # Tools multi-cluster (podem estar em mais de um)
    manager.register_tool(TakeScreenshotTool(), ["WEB", "SYSTEM"])
    
    return manager


if __name__ == "__main__":
    # Teste do ClusterManager
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]🗂️  CLUSTER MANAGER TEST[/bold cyan]\n\n"
        "[yellow]Sistema de organização de ferramentas por domínio[/yellow]",
        border_style="cyan"
    ))
    
    # Criar manager
    manager = create_default_cluster_manager()
    
    # Mostrar estatísticas
    console.print("\n[bold]📊 Estatísticas dos Clusters:[/bold]\n")
    stats = manager.get_cluster_stats()
    
    table = Table(title="Distribuição de Tools por Cluster")
    table.add_column("Cluster", style="cyan", no_wrap=True)
    table.add_column("Qtd Tools", style="green")
    table.add_column("Descrição", style="yellow")
    
    for cluster_name, count in stats.items():
        description = ClusterManager.get_cluster_description(cluster_name)
        table.add_row(cluster_name, str(count), description[:50] + "...")
    
    console.print(table)
    
    # Testar sugestão de clusters
    console.print("\n[bold]🎯 Teste de Sugestão de Clusters:[/bold]\n")
    
    test_tasks = [
        "Calculate the square root of 144",
        "Open Wikipedia and find information about Python",
        "Analyze the CSV file sales_data.csv",
        "Translate 'Hello World' to Spanish",
        "Send an email to john@example.com"
    ]
    
    for task in test_tasks:
        suggested = manager.suggest_clusters_for_task(task)
        console.print(f"[cyan]Task:[/cyan] {task}")
        console.print(f"[green]→ Clusters:[/green] {', '.join(suggested[:3])}\n")
    
    # Testar recuperação de tools
    console.print("\n[bold]🔧 Tools do Cluster MATH:[/bold]")
    math_tools = manager.get_tools_by_clusters(["MATH"])
    for tool in math_tools:
        console.print(f"  • {tool.name}")
    
    console.print("\n[bold]🌐 Tools do Cluster WEB:[/bold]")
    web_tools = manager.get_tools_by_clusters(["WEB"])
    for tool in web_tools:
        console.print(f"  • {tool.name}")
    
    console.print("\n[green]✅ Teste concluído![/green]\n")
