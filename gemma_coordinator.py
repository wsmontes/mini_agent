#!/usr/bin/env python3
"""
Gemma Coordinator - Usa o Qwen Agent como um usuário inteligente

ARQUITETURA CORRETA:
- Qwen Agent: Já existe (agent.py), recebe query, executa tools, retorna resultado
- Gemma: Atua como USUÁRIO inteligente do Qwen Agent
  - Faz queries sequenciais ao Qwen
  - Analisa resultados
  - Decide próximas queries
  - Contorna problemas
  - Formula resposta final

É como ter um assistente (Gemma) usando uma ferramenta (Qwen Agent)
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from agent import QwenAgent  # O Qwen agent que já funciona!
from outlines_agent import OutlinesQwenAgent  # Agent melhorado com structured generation

console = Console()


class GemmaCoordinator:
    """
    Gemma atua como usuário inteligente do Qwen Agent.
    Faz queries sequenciais, analisa resultados, contorna problemas.
    """
    
    @staticmethod
    def _robust_json_parse(content: str, max_retries: int = 2) -> Tuple[Optional[Dict], str]:
        """
        Extrai e parseia JSON de forma robusta, com fallbacks.
        
        Args:
            content: Conteúdo que deve conter JSON
            max_retries: Número de tentativas de limpeza
            
        Returns:
            Tupla (dict_parseado ou None, erro_mensagem)
        """
        # Tentar parsear diretamente
        try:
            return json.loads(content), ""
        except json.JSONDecodeError:
            pass
        
        # Extrair JSON de markdown code blocks
        if "```json" in content:
            try:
                json_str = content.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str), ""
            except (IndexError, json.JSONDecodeError):
                pass
        elif "```" in content:
            try:
                json_str = content.split("```")[1].split("```")[0].strip()
                return json.loads(json_str), ""
            except (IndexError, json.JSONDecodeError):
                pass
        
        # Buscar por objeto JSON no texto
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match), ""
            except json.JSONDecodeError:
                continue
        
        # Tentar corrigir strings não terminadas
        for attempt in range(max_retries):
            try:
                # Adicionar aspas faltantes
                fixed = content.strip()
                if fixed.count('"') % 2 != 0:
                    fixed += '"'
                if fixed.count('{') > fixed.count('}'):
                    fixed += '}' * (fixed.count('{') - fixed.count('}'))
                
                return json.loads(fixed), ""
            except json.JSONDecodeError as e:
                if attempt == max_retries - 1:
                    return None, f"JSON parsing failed after {max_retries} attempts: {str(e)}"
        
        return None, "Could not extract valid JSON from response"
    
    @staticmethod
    def _extract_fallback_from_text(content: str, expected_fields: List[str]) -> Dict[str, Any]:
        """
        Extrai informações do texto quando JSON parsing falha.
        
        Args:
            content: Texto da resposta
            expected_fields: Campos que deveriam estar no JSON
            
        Returns:
            Dict com campos extraídos do texto
        """
        result = {}
        content_lower = content.lower()
        
        if "action" in expected_fields:
            # Check for complete/query_agent keywords
            if "complete" in content_lower or "finished" in content_lower or "done" in content_lower:
                result["action"] = "complete"
            else:
                result["action"] = "query_agent"
        
        if "query_for_agent" in expected_fields:
            # Try to extract instruction
            lines = [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 10]
            result["query_for_agent"] = lines[0] if lines else "Continue with the task"
        
        if "final_answer" in expected_fields:
            result["final_answer"] = content[:500]  # First 500 chars
        
        if "reasoning" in expected_fields:
            reasoning_match = re.search(r'reason(?:ing)?[:\s]+([^\n]+)', content, re.IGNORECASE)
            result["reasoning"] = reasoning_match.group(1).strip() if reasoning_match else "Extracted from text"
        
        return result
    
    def __init__(
        self,
        gemma_model: str = "google/gemma-3-4b",
        qwen_agent: OutlinesQwenAgent = None,  # Usar agent melhorado
        base_url: str = "http://localhost:1234/v1",
        max_iterations: int = 15,
        verbose: bool = True
    ):
        self.gemma_model = gemma_model
        self.qwen_agent = qwen_agent  # Agent já configurado
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        self.client = OpenAI(base_url=base_url, api_key="lm-studio")
        
        self.conversation_history = []
        
        if verbose:
            console.print(Panel.fit(
                f"[bold cyan]🎯 Gemma Coordinator System[/bold cyan]\n"
                f"[yellow]Coordenador:[/yellow] {gemma_model} (atua como usuário)\n"
                f"[yellow]Executor:[/yellow] Qwen Agent (processa queries)\n"
                f"[yellow]Max Iterations:[/yellow] {max_iterations}",
                border_style="cyan"
            ))
    
    def _call_gemma(
        self,
        user_query: str,
        conversation_history: List[Dict],
        iteration: int
    ) -> Dict[str, Any]:
        """
        Gemma decide próxima query para o Qwen ou se está completo.
        
        Retorna:
        {
            "action": "query_agent" ou "complete",
            "query_for_agent": "query para o Qwen" (se query_agent),
            "final_answer": "resposta final" (se complete),
            "reasoning": "explicação"
        }
        """
        
        # Construir histórico da conversa
        history_text = ""
        if conversation_history:
            history_text = "\n\nConversation with the agent so far:\n"
            for i, turn in enumerate(conversation_history, 1):
                history_text += f"\n{i}. YOU ASKED: {turn['query']}\n"
                history_text += f"   AGENT REPLIED: {str(turn['response'])[:300]}...\n"
        
        prompt = f"""You are coordinating with an AI agent to answer a user's question. 

UNDERSTANDING THE AGENT:
The agent is a tool executor - it can perform actions but doesn't "answer questions" directly.
Think of it like a helpful assistant that can:
- Open web pages and extract their content
- Click on links to navigate between pages  
- Perform calculations
- Convert currencies
- Take screenshots
- And other specific actions

When you ask the agent to do something, it will execute the action and report back what happened or what it found.

HOW TO COMMUNICATE WITH THE AGENT:
✓ Good: "Open the Wikipedia page for Python"
✓ Good: "Get the content from the current page"
✓ Good: "Click on the link that says 'Guido van Rossum'"
✓ Good: "Calculate 25 squared"

✗ Bad: "Who created Python?" (agent can't answer, it can only DO things)
✗ Bad: "What's on the page?" (ask it to GET the content instead)

USER'S ORIGINAL QUESTION: {user_query}
{history_text}

YOUR JOB:
1. Look at what the user wants to know
2. Check what information you already have from previous agent responses
3. Decide: Do you have enough to answer the user? Or do you need the agent to DO something else?

Respond with JSON:
{{
  "action": "query_agent" or "complete",
  "reasoning": "explain what you know so far and what you're doing",
  "query_for_agent": "if query_agent: tell the agent what ACTION to perform",
  "final_answer": "if complete: answer the user's question based on what you learned"
}}

IMPORTANT:
- Ask for ONE action at a time
- Use the information from previous responses to decide next steps
- When you have enough information, provide a complete answer to the user
- If something fails, try a different approach"""

        try:
            response = self.client.chat.completions.create(
                model=self.gemma_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strategic coordinator working with an AI agent. You ask the agent to perform tasks and synthesize information from its responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Use robust JSON parsing
            decision, error = self._robust_json_parse(content)
            
            if decision is None:
                if self.verbose:
                    console.print(f"[yellow]⚠ JSON parse error: {error}. Using text fallback.[/yellow]")
                decision = self._extract_fallback_from_text(content, ["action", "reasoning", "query_for_agent", "final_answer"])
            
            if self.verbose:
                console.print(f"\n[bold yellow]🧠 GEMMA (Iteração {iteration})[/bold yellow]")
                table = Table(show_header=False, box=None)
                table.add_column("Field", style="cyan", width=15)
                table.add_column("Value", style="white")
                
                action_emoji = "✅" if decision["action"] == "complete" else "🔄"
                table.add_row("Ação", f"{action_emoji} {decision['action']}")
                table.add_row("Raciocínio", decision.get("reasoning", "")[:200])
                
                if decision["action"] == "query_agent":
                    table.add_row("Query p/ Agent", f"[green]{decision.get('query_for_agent', '')}[/green]")
                else:
                    table.add_row("Resposta Final", decision.get("final_answer", "")[:200])
                
                console.print(table)
            
            return decision
            
        except Exception as e:
            console.print(f"[red]✗ Erro no Gemma: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())
            return {
                "action": "complete",
                "final_answer": f"Error in coordination: {str(e)}",
                "reasoning": "Error occurred"
            }
    
    def _call_qwen_agent(self, query: str) -> str:
        """
        Chama o Qwen Agent (como um usuário faria).
        Retorna a resposta do agent.
        """
        
        if self.verbose:
            console.print(f"\n[bold cyan]🤖 QWEN AGENT[/bold cyan]")
            console.print(f"[yellow]Processando:[/yellow] {query}")
        
        try:
            # Usar o agent.py que já funciona
            response = self.qwen_agent.query(query)
            
            if self.verbose:
                response_preview = response[:300] + "..." if len(response) > 300 else response
                console.print(f"[green]✓ Resposta:[/green]")
                console.print(Panel(response_preview, border_style="green"))
            
            return response
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if self.verbose:
                console.print(f"[red]✗ Erro no Agent: {e}[/red]")
            return error_msg
    
    def query(self, user_query: str) -> str:
        """
        Processa query do usuário usando Gemma como coordenador.
        Gemma faz queries sequenciais ao Qwen Agent até ter a resposta.
        """
        
        console.print("\n" + "="*70)
        console.print(f"[bold cyan]💬 USER QUERY:[/bold cyan] {user_query}")
        console.print("="*70)
        
        self.conversation_history = []
        
        for iteration in range(1, self.max_iterations + 1):
            console.print(f"\n[bold magenta]{'='*70}[/bold magenta]")
            console.print(f"[bold magenta]ITERAÇÃO {iteration}/{self.max_iterations}[/bold magenta]")
            console.print(f"[bold magenta]{'='*70}[/bold magenta]")
            
            # 1. Gemma decide o que fazer
            decision = self._call_gemma(user_query, self.conversation_history, iteration)
            
            # 2. Se está completo, retornar resposta
            if decision["action"] == "complete":
                final_answer = decision.get("final_answer", "Task completed")
                
                if self.verbose:
                    console.print("\n[bold green]✅ MISSÃO COMPLETA![/bold green]")
                    console.print(Panel(final_answer, title="Resposta Final", border_style="green"))
                
                return final_answer
            
            # 3. Se precisa fazer query, chamar o Qwen Agent
            query_for_agent = decision.get("query_for_agent")
            if not query_for_agent:
                console.print("[yellow]⚠️  Gemma não especificou query para o agent[/yellow]")
                break
            
            # 4. Chamar o Agent (Qwen)
            agent_response = self._call_qwen_agent(query_for_agent)
            
            # 5. Adicionar ao histórico
            self.conversation_history.append({
                "iteration": iteration,
                "query": query_for_agent,
                "response": agent_response
            })
        
        # Limite atingido
        console.print(f"\n[yellow]⚠️  Limite de {self.max_iterations} iterações atingido[/yellow]")
        
        # Pedir resposta final ao Gemma baseado no que conseguiu
        final_decision = self._call_gemma(user_query, self.conversation_history, self.max_iterations + 1)
        return final_decision.get("final_answer", "Maximum iterations reached. Unable to complete task.")


def main():
    """Exemplo de uso."""
    from tools.general_tools import AdvancedCalculatorTool, CurrencyConverterTool
    from tools.browser_tools import (
        OpenURLTool, GetPageContentTool, ClickElementTool,
        FillFormTool, TakeScreenshotTool, CloseBrowserTool
    )
    
    # Criar o Qwen Agent melhorado com Outlines
    qwen_agent = OutlinesQwenAgent(
        model_name="qwen3-4b-toolcalling-codex",
        base_url="http://localhost:1234/v1",
        temperature=0.2,
        verbose=False  # Gemma mostra os resultados
    )
    
    # Registrar ferramentas no Qwen
    qwen_agent.register_tool(AdvancedCalculatorTool())
    qwen_agent.register_tool(CurrencyConverterTool())
    qwen_agent.register_tool(OpenURLTool())
    qwen_agent.register_tool(GetPageContentTool())
    qwen_agent.register_tool(ClickElementTool())
    qwen_agent.register_tool(FillFormTool())
    qwen_agent.register_tool(TakeScreenshotTool())
    qwen_agent.register_tool(CloseBrowserTool())
    
    # Criar o Coordenador Gemma
    coordinator = GemmaCoordinator(
        gemma_model="google/gemma-3-4b",
        qwen_agent=qwen_agent,
        max_iterations=15,
        verbose=True
    )
    
    # Teste
    result = coordinator.query("Calcule 15 ao quadrado e converta para EUR")
    console.print(f"\n[bold]RESULTADO FINAL:[/bold] {result}")


if __name__ == "__main__":
    main()
