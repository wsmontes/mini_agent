"""
Main entry point for the Qwen3 Agent.
Interactive CLI for chatting with the agent.
"""

from agent import QwenAgent
from tools import (
    WeatherTool,
    CurrentWeatherTool,
    ForecastWeatherTool,
    CalculatorTool,
    WebSearchTool,
    FileReadTool,
    FileListTool
)
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import sys

console = Console()


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔══════════════════════════════════════════╗
    ║   🤖 Qwen3-4B Function Calling Agent    ║
    ║                                          ║
    ║   Powered by LM Studio                   ║
    ║   Model: Qwen3-4B-toolcalling           ║
    ╚══════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def setup_agent():
    """Initialize agent with tools."""
    console.print("\n[yellow]⚙️  Initializing agent...[/yellow]")
    
    try:
        # Create agent
        agent = QwenAgent(
            enable_thinking=False,  # Set to True for reasoning mode
            auto_execute_tools=True
        )
        
        # Set system message
        agent.set_system_message(
            "You are a helpful AI assistant with access to various tools. "
            "Use the tools when needed to help answer user questions accurately. "
            "Always be concise and helpful."
        )
        
        # Register tools
        console.print("[yellow]📦 Loading tools...[/yellow]")
        
        agent.register_tool(CurrentWeatherTool())
        agent.register_tool(ForecastWeatherTool())
        agent.register_tool(CalculatorTool())
        agent.register_tool(WebSearchTool())
        agent.register_tool(FileListTool())
        
        console.print(f"[green]✓ Loaded {len(agent.tools)} tools[/green]")
        
        # List available tools
        console.print("\n[cyan]Available tools:[/cyan]")
        for tool_name in agent.tools.keys():
            console.print(f"  • {tool_name}")
            
        return agent
        
    except Exception as e:
        console.print(f"\n[red]❌ Error initializing agent:[/red] {e}")
        console.print("\n[yellow]Make sure:[/yellow]")
        console.print("  1. LM Studio is running")
        console.print("  2. A model is loaded")
        console.print("  3. Local server is started (default: http://localhost:1234)")
        sys.exit(1)


def interactive_mode(agent: QwenAgent):
    """Run interactive chat mode."""
    console.print("\n[green]✨ Agent ready! Type your message or 'help' for commands[/green]")
    console.print("[dim]Commands: help, clear, exit, quit[/dim]\n")
    
    while True:
        try:
            # Get user input
            user_input = console.input("[bold blue]You:[/bold blue] ").strip()
            
            if not user_input:
                continue
                
            # Handle commands
            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("\n[cyan]👋 Goodbye![/cyan]")
                break
                
            elif user_input.lower() == "clear":
                agent.reset_conversation()
                console.print("[yellow]🔄 Conversation cleared[/yellow]\n")
                continue
                
            elif user_input.lower() == "help":
                show_help()
                continue
                
            # Process query
            console.print("\n[dim]🤔 Thinking...[/dim]")
            
            response = agent.query(user_input, return_metadata=True)
            
            # Display response
            if response.get("success"):
                content = response.get("content", "")
                
                # Show tool calls if any
                if tool_calls := response.get("tool_calls"):
                    console.print("\n[yellow]🛠️  Tool calls:[/yellow]")
                    for tc in tool_calls:
                        fn_name = tc.get("function_name", "unknown")
                        success = "✓" if tc.get("success") else "✗"
                        console.print(f"  {success} {fn_name}")
                        
                # Show response
                console.print(f"\n[bold green]Agent:[/bold green] {content}\n")
            else:
                error = response.get("error", "Unknown error")
                console.print(f"\n[red]❌ Error:[/red] {error}\n")
                
        except KeyboardInterrupt:
            console.print("\n\n[cyan]👋 Goodbye![/cyan]")
            break
            
        except Exception as e:
            console.print(f"\n[red]❌ Error:[/red] {e}\n")


def show_help():
    """Show help information."""
    help_text = """
    **Available Commands:**
    
    • `help` - Show this help message
    • `clear` - Clear conversation history
    • `exit`, `quit` - Exit the program
    
    **Example Questions:**
    
    • "What's the weather in San Francisco?"
    • "Calculate the square root of 144"
    • "Search the web for Python tutorials"
    • "List files in the current directory"
    
    **Tips:**
    
    • The agent will automatically use tools when needed
    • You can ask follow-up questions
    • Conversation history is maintained until you 'clear'
    """
    console.print(Panel(Markdown(help_text), title="Help", border_style="cyan"))


def main():
    """Main entry point."""
    print_banner()
    
    agent = setup_agent()
    interactive_mode(agent)


if __name__ == "__main__":
    main()
