#!/usr/bin/env python3
"""
Demonstração das ferramentas de navegação web com browser real.

Este script mostra como usar as ferramentas de automação de browser que navegam
de verdade, com o browser visível para você acompanhar tudo que está acontecendo.

Uso:
    python examples/browser_demo.py [modo]
    
Modos disponíveis:
    basic       - Navegação básica (abre site e faz screenshot)
    search      - Busca no Google
    wikipedia   - Navega na Wikipedia
    form        - Preenche formulário de exemplo
    scraping    - Extrai conteúdo de página
    interactive - Modo interativo (digite comandos)
    all         - Executa todos os demos
"""

import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.browser_tools import (
    OpenURLTool,
    GetPageContentTool,
    ClickElementTool,
    FillFormTool,
    TakeScreenshotTool,
    ScrollPageTool,
    FindElementsTool,
    ExecuteJavaScriptTool,
    GoBackTool,
    GoForwardTool,
    CloseBrowserTool,
)
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint
import json

console = Console()


def print_section(title: str):
    """Imprime um cabeçalho de seção."""
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold yellow]{title}[/bold yellow]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")


def print_result(tool_name: str, result: dict):
    """Imprime o resultado de uma ferramenta."""
    console.print(f"[bold green]✓ {tool_name}[/bold green]")
    result_json = json.dumps(result, indent=2, ensure_ascii=False)
    syntax = Syntax(result_json, "json", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title=f"Resultado", border_style="green"))


def demo_basic():
    """Demo 1: Navegação básica - abre site e tira screenshot."""
    print_section("DEMO 1: Navegação Básica")
    
    console.print("[cyan]1. Abrindo site Example.com...[/cyan]")
    open_tool = OpenURLTool()
    result = open_tool.execute(url="https://example.com")
    print_result("OpenURLTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]2. Obtendo conteúdo da página...[/cyan]")
    content_tool = GetPageContentTool()
    result = content_tool.execute()
    print_result("GetPageContentTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]3. Tirando screenshot...[/cyan]")
    screenshot_tool = TakeScreenshotTool()
    result = screenshot_tool.execute(filename="example_site.png")
    print_result("TakeScreenshotTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]4. Fechando browser...[/cyan]")
    close_tool = CloseBrowserTool()
    result = close_tool.execute()
    print_result("CloseBrowserTool", result)


def demo_search():
    """Demo 2: Busca no Google."""
    print_section("DEMO 2: Busca no Google")
    
    console.print("[cyan]1. Abrindo Google...[/cyan]")
    open_tool = OpenURLTool()
    result = open_tool.execute(url="https://www.google.com")
    print_result("OpenURLTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]2. Preenchendo campo de busca...[/cyan]")
    fill_tool = FillFormTool()
    result = fill_tool.execute(
        selector_type="name",
        selector_value="q",
        text="Python programming",
        submit=True
    )
    print_result("FillFormTool", result)
    time.sleep(3)
    
    console.print("\n[cyan]3. Tirando screenshot dos resultados...[/cyan]")
    screenshot_tool = TakeScreenshotTool()
    result = screenshot_tool.execute(filename="google_results.png")
    print_result("TakeScreenshotTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]4. Fechando browser...[/cyan]")
    close_tool = CloseBrowserTool()
    result = close_tool.execute()
    print_result("CloseBrowserTool", result)


def demo_wikipedia():
    """Demo 3: Navega na Wikipedia."""
    print_section("DEMO 3: Wikipedia")
    
    console.print("[cyan]1. Abrindo página principal da Wikipedia...[/cyan]")
    open_tool = OpenURLTool()
    result = open_tool.execute(url="https://en.wikipedia.org")
    print_result("OpenURLTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]2. Buscando por 'Artificial Intelligence'...[/cyan]")
    fill_tool = FillFormTool()
    result = fill_tool.execute(
        selector_type="name",
        selector_value="search",
        text="Artificial Intelligence",
        submit=True
    )
    print_result("FillFormTool", result)
    time.sleep(3)
    
    console.print("\n[cyan]3. Extraindo conteúdo da página...[/cyan]")
    content_tool = GetPageContentTool()
    result = content_tool.execute()
    # Mostrar apenas os primeiros 500 caracteres do texto
    if result.get("success"):
        text_preview = result["text_content"][:500] + "..."
        result_preview = {
            "success": result["success"],
            "text_preview": text_preview,
            "num_links": result["num_links"],
            "num_images": result["num_images"]
        }
        print_result("GetPageContentTool", result_preview)
    else:
        print_result("GetPageContentTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]4. Rolando página para baixo...[/cyan]")
    scroll_tool = ScrollPageTool()
    result = scroll_tool.execute(direction="down", amount=500)
    print_result("ScrollPageTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]5. Tirando screenshot...[/cyan]")
    screenshot_tool = TakeScreenshotTool()
    result = screenshot_tool.execute(filename="wikipedia_ai.png")
    print_result("TakeScreenshotTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]6. Fechando browser...[/cyan]")
    close_tool = CloseBrowserTool()
    result = close_tool.execute()
    print_result("CloseBrowserTool", result)


def demo_form():
    """Demo 4: Preenche formulário de exemplo."""
    print_section("DEMO 4: Preenchimento de Formulário")
    
    console.print("[cyan]1. Abrindo página com formulário...[/cyan]")
    open_tool = OpenURLTool()
    result = open_tool.execute(url="https://httpbin.org/forms/post")
    print_result("OpenURLTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]2. Preenchendo campo 'custname'...[/cyan]")
    fill_tool = FillFormTool()
    result = fill_tool.execute(
        selector_type="name",
        selector_value="custname",
        text="João Silva"
    )
    print_result("FillFormTool", result)
    time.sleep(1)
    
    console.print("\n[cyan]3. Preenchendo campo 'custtel'...[/cyan]")
    result = fill_tool.execute(
        selector_type="name",
        selector_value="custtel",
        text="11999998888"
    )
    print_result("FillFormTool", result)
    time.sleep(1)
    
    console.print("\n[cyan]4. Preenchendo campo 'custemail'...[/cyan]")
    result = fill_tool.execute(
        selector_type="name",
        selector_value="custemail",
        text="joao@example.com"
    )
    print_result("FillFormTool", result)
    time.sleep(1)
    
    console.print("\n[cyan]5. Tirando screenshot do formulário preenchido...[/cyan]")
    screenshot_tool = TakeScreenshotTool()
    result = screenshot_tool.execute(filename="form_filled.png")
    print_result("TakeScreenshotTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]6. Fechando browser...[/cyan]")
    close_tool = CloseBrowserTool()
    result = close_tool.execute()
    print_result("CloseBrowserTool", result)


def demo_scraping():
    """Demo 5: Web scraping - extrai dados de uma página."""
    print_section("DEMO 5: Web Scraping")
    
    console.print("[cyan]1. Abrindo página de exemplo...[/cyan]")
    open_tool = OpenURLTool()
    result = open_tool.execute(url="https://quotes.toscrape.com/")
    print_result("OpenURLTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]2. Encontrando todas as citações...[/cyan]")
    find_tool = FindElementsTool()
    result = find_tool.execute(
        selector_type="class",
        selector_value="quote",
        max_results=10
    )
    print_result("FindElementsTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]3. Executando JavaScript para extrair citações...[/cyan]")
    js_tool = ExecuteJavaScriptTool()
    js_code = """
    const quotes = [];
    document.querySelectorAll('.quote').forEach((quote, idx) => {
        if (idx < 5) {  // Primeiras 5 citações
            const text = quote.querySelector('.text').innerText;
            const author = quote.querySelector('.author').innerText;
            quotes.push({text, author});
        }
    });
    return quotes;
    """
    result = js_tool.execute(script=js_code)
    print_result("ExecuteJavaScriptTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]4. Clicando em 'Next' para próxima página...[/cyan]")
    click_tool = ClickElementTool()
    result = click_tool.execute(
        selector_type="link_text",
        selector_value="Next"
    )
    print_result("ClickElementTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]5. Voltando para página anterior...[/cyan]")
    back_tool = GoBackTool()
    result = back_tool.execute()
    print_result("GoBackTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]6. Avançando novamente...[/cyan]")
    forward_tool = GoForwardTool()
    result = forward_tool.execute()
    print_result("GoForwardTool", result)
    time.sleep(2)
    
    console.print("\n[cyan]7. Fechando browser...[/cyan]")
    close_tool = CloseBrowserTool()
    result = close_tool.execute()
    print_result("CloseBrowserTool", result)


def demo_interactive():
    """Demo 6: Modo interativo - usuário pode digitar comandos."""
    print_section("DEMO 6: Modo Interativo")
    
    console.print("[yellow]Modo Interativo - Digite comandos:[/yellow]")
    console.print("[cyan]  open <url>     - Abre uma URL[/cyan]")
    console.print("[cyan]  content        - Mostra conteúdo da página[/cyan]")
    console.print("[cyan]  screenshot     - Tira screenshot[/cyan]")
    console.print("[cyan]  scroll up|down - Rola a página[/cyan]")
    console.print("[cyan]  back           - Volta página[/cyan]")
    console.print("[cyan]  forward        - Avança página[/cyan]")
    console.print("[cyan]  quit           - Sai e fecha browser[/cyan]")
    console.print()
    
    open_tool = OpenURLTool()
    content_tool = GetPageContentTool()
    screenshot_tool = TakeScreenshotTool()
    scroll_tool = ScrollPageTool()
    back_tool = GoBackTool()
    forward_tool = GoForwardTool()
    close_tool = CloseBrowserTool()
    
    while True:
        try:
            command = console.input("[bold green]>>> [/bold green]").strip()
            
            if not command:
                continue
                
            if command == "quit":
                console.print("[yellow]Fechando browser...[/yellow]")
                result = close_tool.execute()
                print_result("CloseBrowserTool", result)
                break
                
            elif command.startswith("open "):
                url = command[5:].strip()
                result = open_tool.execute(url=url)
                print_result("OpenURLTool", result)
                
            elif command == "content":
                result = content_tool.execute()
                # Mostrar preview
                if result.get("success"):
                    text_preview = result["text_content"][:300] + "..."
                    result_preview = {
                        "success": result["success"],
                        "text_preview": text_preview,
                        "num_links": result["num_links"],
                        "num_images": result["num_images"]
                    }
                    print_result("GetPageContentTool", result_preview)
                else:
                    print_result("GetPageContentTool", result)
                    
            elif command == "screenshot":
                result = screenshot_tool.execute()
                print_result("TakeScreenshotTool", result)
                
            elif command.startswith("scroll "):
                direction = command[7:].strip()
                result = scroll_tool.execute(direction=direction)
                print_result("ScrollPageTool", result)
                
            elif command == "back":
                result = back_tool.execute()
                print_result("GoBackTool", result)
                
            elif command == "forward":
                result = forward_tool.execute()
                print_result("GoForwardTool", result)
                
            else:
                console.print("[red]Comando não reconhecido![/red]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrompido pelo usuário. Fechando browser...[/yellow]")
            close_tool.execute()
            break
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")


def main():
    """Função principal."""
    console.print(Panel.fit(
        "[bold cyan]🌐 Demo de Ferramentas de Browser[/bold cyan]\n"
        "[yellow]Browser visível - Acompanhe tudo que acontece![/yellow]",
        border_style="cyan"
    ))
    
    if len(sys.argv) < 2:
        mode = "basic"
    else:
        mode = sys.argv[1].lower()
    
    try:
        if mode == "basic":
            demo_basic()
        elif mode == "search":
            demo_search()
        elif mode == "wikipedia":
            demo_wikipedia()
        elif mode == "form":
            demo_form()
        elif mode == "scraping":
            demo_scraping()
        elif mode == "interactive":
            demo_interactive()
        elif mode == "all":
            console.print("[bold yellow]Executando todos os demos...[/bold yellow]")
            console.print("[cyan]Pressione Ctrl+C para pular para o próximo[/cyan]\n")
            
            try:
                demo_basic()
                console.input("\n[yellow]Pressione Enter para continuar...[/yellow]")
            except KeyboardInterrupt:
                pass
            
            try:
                demo_search()
                console.input("\n[yellow]Pressione Enter para continuar...[/yellow]")
            except KeyboardInterrupt:
                pass
            
            try:
                demo_wikipedia()
                console.input("\n[yellow]Pressione Enter para continuar...[/yellow]")
            except KeyboardInterrupt:
                pass
            
            try:
                demo_form()
                console.input("\n[yellow]Pressione Enter para continuar...[/yellow]")
            except KeyboardInterrupt:
                pass
            
            try:
                demo_scraping()
            except KeyboardInterrupt:
                pass
        else:
            console.print(f"[red]Modo desconhecido: {mode}[/red]")
            console.print("[yellow]Modos disponíveis: basic, search, wikipedia, form, scraping, interactive, all[/yellow]")
            return
        
        console.print("\n[bold green]✓ Demo concluído![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro durante demo: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        
        # Garantir que o browser seja fechado
        try:
            close_tool = CloseBrowserTool()
            close_tool.execute()
        except:
            pass


if __name__ == "__main__":
    main()
