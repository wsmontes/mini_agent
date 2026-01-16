#!/usr/bin/env python3
"""
GEMMA CLUSTER COORDINATOR
Coordenador que usa Gemma para selecionar clusters e Qwen para executar
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

from cluster_manager import ClusterManager


class GemmaClusterCoordinator:
    """
    Coordenador que:
    1. Usa Gemma para identificar qual(is) cluster(s) a tarefa pertence
    2. Carrega apenas tools relevantes daquele cluster
    3. Usa Qwen Agent com tools filtradas
    4. Itera até completar a tarefa
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
        
        # Padrões comuns de extração
        if "clusters" in expected_fields:
            # Buscar por nomes de clusters
            cluster_names = ["WEB", "MATH", "DATA", "TEXT", "COMMUNICATION", "SYSTEM", "CODE"]
            found_clusters = [c for c in cluster_names if c.lower() in content_lower or c in content]
            if found_clusters:
                result["clusters"] = found_clusters
            else:
                result["clusters"] = ["WEB"]  # Default seguro
            
            # Extrair reasoning
            reasoning_match = re.search(r'reason(?:ing)?[:\s]+([^\n]+)', content, re.IGNORECASE)
            result["reasoning"] = reasoning_match.group(1).strip() if reasoning_match else "Fallback reasoning from text"
        
        if "instruction" in expected_fields:
            # Buscar por instrução após marcadores comuns
            instruction_match = re.search(r'instruction[:\s]+([^\n]+)', content, re.IGNORECASE)
            if instruction_match:
                result["instruction"] = instruction_match.group(1).strip()
            else:
                # Pegar primeira frase significativa
                lines = [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 10]
                result["instruction"] = lines[0] if lines else "Execute the task"
        
        if "completed" in expected_fields:
            # Análise de sentimento para completed
            positive_words = ["success", "completed", "done", "achieved", "✅", "yes", "true"]
            negative_words = ["failed", "error", "not completed", "unsuccessful", "❌", "no", "false"]
            
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            result["completed"] = positive_count > negative_count
            result["reasoning"] = f"Based on text analysis: {positive_count} positive vs {negative_count} negative indicators"
            result["next_action"] = "next_subtask" if result["completed"] else "reformulate"
        
        if "achieved" in expected_fields:
            # Similar ao completed
            positive_words = ["success", "achieved", "complete", "✅", "yes", "true", "correct"]
            negative_words = ["failed", "not achieved", "incomplete", "❌", "no", "false", "wrong"]
            
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            result["achieved"] = positive_count > negative_count
            result["evidence"] = f"Text analysis: {positive_count} positive vs {negative_count} negative indicators"
        
        return result
    
    def __init__(
        self,
        cluster_manager: ClusterManager,
        qwen_agent,
        gemma_model: str = "google/gemma-3-4b",
        base_url: str = "http://localhost:1234/v1",
        temperature: float = 0.3,
        max_iterations: int = 15,
        verbose: bool = True
    ):
        """
        Inicializa o coordenador com clusters
        
        Args:
            cluster_manager: Gerenciador de clusters com tools registradas
            qwen_agent: Agente Qwen para executar as tools
            gemma_model: Nome do modelo Gemma
            base_url: URL da API do LM Studio
            temperature: Temperatura para geração (planejador usa isso, executor usa menor)
            max_iterations: Máximo de iterações
            verbose: Se deve imprimir informações detalhadas
        """
        self.cluster_manager = cluster_manager
        self.qwen_agent = qwen_agent
        self.gemma_model = gemma_model
        # BEST PRACTICE: Temperaturas diferenciadas por função
        self.planner_temperature = max(temperature, 0.4)  # Planejador mais criativo
        self.executor_temperature = 0.1  # Executor mais determinístico
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.console = Console() if verbose else None
        
        # Cliente Gemma
        self.gemma_client = OpenAI(
            base_url=base_url,
            api_key="not-needed"
        )
        
        # BEST PRACTICE: Skill Harvesting - memorizar padrões bem-sucedidos
        self.successful_patterns = []  # Lista de (task_type, action_sequence, success_rate)
        
        # Histórico da conversa
        self.conversation_history = []
        
        # SLIDING WINDOW DE CLUSTERS: mantém ferramentas de clusters recentes
        self.cluster_history = []  # Lista de clusters usados recentemente
        self.cluster_window_size = 2  # Manter ferramentas dos últimos 2 conjuntos de clusters
        
        # MEMÓRIA COMPARTILHADA: estado do navegador e dados extraídos
        self.shared_context = {
            "current_url": None,
            "current_page_title": None,
            "visited_pages": [],
            "extracted_data": {},
            "last_action": None,
            "page_structure": None  # Dynamic page structure discovery
        }
        
        # TODO LIST: tarefas e subtarefas estruturadas
        self.todo_list = {
            "main_goal": "",
            "tasks": []  # Lista de {"id": int, "description": str, "status": "pending|in_progress|done", "subtasks": []}
        }
        self.task_counter = 0
        self.current_task_id = None  # ID da tarefa atual sendo executada
        self.current_subtask_index = 0  # Índice da subtask atual dentro da tarefa
        
        # SISTEMA DE ESCALAÇÃO DE ERROS: rastreia falhas e decide quando escalar
        self.error_tracking = {
            "subtask_failures": [],  # Lista de {"subtask": str, "errors": [], "attempts": int}
            "task_revision_count": 0,  # Quantas vezes a task atual foi revisada
            "todo_revision_count": 0,   # Quantas vezes o TODO foi revisado
            "last_escalation_level": None,  # "subtask", "task", ou "todo"
        }
        
        # Detecção automática de loops e travamentos
        self.loop_detector = {
            "last_actions": [],  # Últimas 5 ações do Qwen
            "precondition_failures": 0,  # Quantas vezes PRECONDITION FAILED foi ignorado
            "identical_action_count": 0,  # Quantas vezes mesma ação foi repetida
        }
        
        # Thresholds para escalação AUTOMÁTICA (não depende de modelo)
        self.IDENTICAL_ACTION_LIMIT = 2  # Se fizer mesma ação 2x, é loop
        self.PRECONDITION_FAILURE_LIMIT = 1  # Se ignorar PRECONDITION 1x, escalar
        self.SUBTASK_RETRY_LIMIT = 3  # Após 3 falhas, escalar para Gemma revisar subtasks
        self.TASK_REVISION_LIMIT = 2   # Após 2 revisões de subtasks, revisar task inteira
        self.TODO_REVISION_LIMIT = 1   # Após 1 revisão de task, revisar TODO
    
    def _call_gemma_cluster_selection(self, user_query: str, consider_history: bool = False) -> Dict[str, Any]:
        """
        Chama Gemma para selecionar clusters relevantes
        
        Args:
            user_query: Query do usuário
            consider_history: Se True, considera histórico para escolher clusters
            
        Returns:
            Dict com clusters selecionados e raciocínio
        """
        # Lista de clusters disponíveis
        cluster_info = []
        for cluster_name in ClusterManager.get_cluster_names():
            description = ClusterManager.get_cluster_description(cluster_name)
            cluster_info.append(f"- {cluster_name}: {description}")
        
        clusters_text = "\n".join(cluster_info)
        
        # Monta histórico se necessário
        history_context = ""
        if consider_history and self.conversation_history:
            recent_history = self.conversation_history[-2:]  # Últimas 2 interações
            history_text = "\n".join([
                f"Step {h['iteration']}: {h['query']}\nResult: {h['response'][:200]}..."
                for h in recent_history
            ])
            history_context = f"\n\nRECENT PROGRESS:\n{history_text}\n\nBased on what we've done so far, what clusters do we need for the NEXT step?"
        
        # BEST PRACTICE: Few-shot examples + Pensamento→Ação explícito
        system_prompt = f"""You are an intelligent task classifier. Your job is to identify which category/cluster a task belongs to.

AVAILABLE CLUSTERS:
{clusters_text}

USE THIS FORMAT:
Thought: [Analyze what the NEXT step requires]
Action: [Select clusters needed]

FEW-SHOT EXAMPLES:

Example 1:
Task: "Search Google for Python creator"
Thought: Need to open a web browser and navigate to Google's website. This requires web navigation tools.
Action: {{"clusters": ["WEB"], "reasoning": "Web navigation needed to open Google"}}

Example 2:
Task: "Calculate the square of 25 and convert to EUR"
Thought: First need mathematical calculation, then currency conversion. Both are math operations.
Action: {{"clusters": ["MATH"], "reasoning": "Math operations for calculation and currency conversion"}}

Example 3:
Task: "Extract data from CSV and search for info online"
Thought: Need data processing tools first, then web tools for searching.
Action: {{"clusters": ["DATA", "WEB"], "reasoning": "DATA for CSV processing, WEB for online search"}}

NOW YOUR TURN:
Given a task, respond with JSON:
{{
    "thought": "What does the NEXT step require?",
    "clusters": ["CLUSTER1", "CLUSTER2"],
    "reasoning": "Brief explanation"
}}

Important: 
- Choose clusters for the NEXT action only
- If task changes (web→calculation), change clusters
- Be specific - max 2-3 clusters"""

        user_prompt = f"""Original task: {user_query}{history_context}

Which cluster(s) should be used?"""

        try:
            response = self.gemma_client.chat.completions.create(
                model=self.gemma_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.planner_temperature,  # Higher temp for planning creativity
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parsing robusto com fallback
            result, error = self._robust_json_parse(content)
            
            if result is None:
                if self.verbose:
                    self.console.print(f"[yellow]⚠ JSON parse error: {error}. Using text fallback.[/yellow]")
                result = self._extract_fallback_from_text(content, ["clusters", "reasoning"])
            
            # Valida clusters
            selected_clusters = result.get("clusters", [])
            valid_clusters = [c for c in selected_clusters if c in ClusterManager.get_cluster_names()]
            
            if not valid_clusters:
                # Fallback: usa sugestão por keywords
                valid_clusters = self.cluster_manager.suggest_clusters_for_task(user_query)[:2]
            
            return {
                "clusters": valid_clusters,
                "reasoning": result.get("reasoning", "")
            }
            
        except Exception as e:
            if self.verbose:
                self.console.print(f"[yellow]⚠ Erro ao chamar Gemma: {e}[/yellow]")
            
            # Fallback: usa sugestão por keywords
            suggested = self.cluster_manager.suggest_clusters_for_task(user_query)[:2]
            return {
                "clusters": suggested if suggested else ["MATH", "TEXT"],
                "reasoning": "Fallback to keyword-based suggestion"
            }
    
    def _call_gemma_decision(self, user_query: str, selected_clusters: List[str]) -> Dict[str, Any]:
        """
        Chama Gemma para decidir próxima ação (similar ao coordinator original)
        
        Args:
            user_query: Query original do usuário
            selected_clusters: Clusters que foram selecionados
            
        Returns:
            Dict com ação e query para o agente (se aplicável)
        """
        # Monta histórico
        history_text = ""
        if self.conversation_history:
            history_text = "\n\n".join([
                f"Iteration {h['iteration']}:\nQuery: {h['query']}\nResponse: {h['response']}"
                for h in self.conversation_history[-3:]  # Últimas 3 iterações
            ])
        
        system_prompt = f"""You are a PROJECT MANAGER coordinating with a TOOL EXECUTOR agent.

The agent has access to tools from these clusters: {', '.join(selected_clusters)}

YOUR MANAGEMENT PROCESS:
1. ANALYZE the latest result from the agent
2. CHECK if it contains what you need for the user's goal
3. DECIDE next action:
   - If you have complete information → action: "complete"
   - If result has errors → try different approach
   - If result is partial → request missing information
   - If stuck → break down into smaller steps

The agent can DO these actions:
- Perform calculations (give exact expression)
- Open web pages (give exact URL)
- Click elements (give link text or selector)
- Extract page content
- Fill forms
- Process text
- Execute system commands

Respond with JSON:
{{
    "action": "query_agent" or "complete",
    "reasoning": "What I learned from previous result and why I'm taking this action",
    "query_for_agent": "Specific executable instruction" (only if action is query_agent),
    "final_answer": "Complete answer to user" (only if action is complete)
}}

CRITICAL - RECOVERY CYCLE:
- If agent returned error → analyze why and try different tool/approach
- If agent returned partial data → extract what's useful and request what's missing
- If agent succeeded → check if goal is met or if more steps needed
- ALWAYS reference previous results in your reasoning

INSTRUCTION QUALITY:
- Give SPECIFIC actions: "Click the link with text 'Guido van Rossum'" not "find Guido"
- Give EXACT parameters: "Open https://en.wikipedia.org/wiki/Python_(programming_language)"
- Break complex tasks: First navigate, then extract, then calculate

TODO LIST:
{self._get_todo_summary()}

BROWSER STATE (shared memory - agent knows this too):
{self._get_context_summary()}
"""

        user_prompt = f"""Original task: {user_query}

Conversation history:
{history_text if history_text else "No previous interactions yet"}

Based on the browser state and results above, what should we do next?"""

        try:
            response = self.gemma_client.chat.completions.create(
                model=self.gemma_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parsing robusto com fallback
            result, error = self._robust_json_parse(content)
            
            if result is None:
                if self.verbose:
                    self.console.print(f"[yellow]⚠ JSON parse error: {error}. Using safe default.[/yellow]")
                # Default seguro: completar
                return {
                    "action": "complete",
                    "reasoning": "Could not parse response, assuming completion",
                    "final_answer": "Task completed with available information"
                }
            
            return result
            
        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]✗ Erro ao chamar Gemma: {e}[/red]")
            return {
                "action": "complete",
                "reasoning": f"Error occurred: {e}",
                "final_answer": f"Sorry, I encountered an error: {e}"
            }
    
    def query_step_by_step(self, user_query: str) -> str:
        """
        NEW WORKFLOW: Processes user query with step-by-step Gemma iteration.
        
        Workflow:
        1. Gemma creates TODO list from user request
        2. For each task:
           a. Gemma breaks into subtasks
           b. For each subtask:
              - Gemma selects clusters
              - Gemma formulates specific instruction
              - Qwen executes
              - Gemma evaluates result
        
        Args:
            user_query: User's request
            
        Returns:
            Final answer
        """
        self.conversation_history = []
        
        if self.verbose:
            self.console.print(Panel.fit(
                f"[bold cyan]🎯 USER QUERY[/bold cyan]\n\n{user_query}",
                border_style="cyan"
            ))
        
        # =====================================================================
        # STEP 1: Gemma creates TODO list
        # =====================================================================
        if self.verbose:
            self.console.print("\n[bold magenta]📋 STEP 1: Creating TODO list[/bold magenta]")
        
        todo_data = self._gemma_create_todo(user_query)
        self._initialize_todo_list(todo_data["main_goal"])
        
        for task_data in todo_data["tasks"]:
            self._add_task(task_data["description"])
        
        if self.verbose:
            self.console.print(Panel(self._get_todo_summary(), title="📋 TODO List", border_style="green"))
        
        # =====================================================================
        # STEP 2: Iterate through tasks
        # =====================================================================
        iteration_count = 0
        
        for task in self.todo_list["tasks"]:
            if iteration_count >= self.max_iterations:
                break
            
            task_id = task["id"]
            self.current_task_id = task_id
            self._update_task_status(task_id, "in_progress")
            
            # Clear page structure for new task context
            self.shared_context["page_structure"] = None
            
            if self.verbose:
                self.console.print(f"\n[bold blue]{'='*60}[/bold blue]")
                self.console.print(f"[bold blue]🎯 TASK {task_id}: {task['description']}[/bold blue]")
                self.console.print(f"[bold blue]{'='*60}[/bold blue]\n")
            
            # =================================================================
            # STEP 2a: Gemma creates subtasks for this task
            # =================================================================
            if self.verbose:
                self.console.print("[bold magenta]📝 Creating subtasks...[/bold magenta]")
            
            # BEST PRACTICE: Verificar se há padrão similar registrado
            similar_pattern = self._get_similar_pattern(task["description"])
            
            if similar_pattern and self.verbose:
                self.console.print(f"[cyan]💡 Found similar pattern with {len(similar_pattern)} steps[/cyan]")
            
            subtasks = self._gemma_create_subtasks(task["description"], hint=similar_pattern)
            task["subtasks"] = subtasks
            
            if self.verbose:
                for i, subtask in enumerate(subtasks, 1):
                    self.console.print(f"   {i}. {subtask}")
            
            # =================================================================
            # STEP 2b: Execute each subtask
            # =================================================================
            for subtask_index, subtask in enumerate(subtasks):
                if iteration_count >= self.max_iterations:
                    break
                
                self.current_subtask_index = subtask_index
                iteration_count += 1
                
                if self.verbose:
                    self.console.print(f"\n[cyan]{'─'*60}[/cyan]")
                    self.console.print(f"[cyan]🔧 Subtask {subtask_index + 1}/{len(subtasks)}: {subtask}[/cyan]")
                    self.console.print(f"[cyan]{'─'*60}[/cyan]")
                
                max_retries = 3
                retry_count = 0
                subtask_completed = False
                
                while not subtask_completed and retry_count < max_retries:
                    # Step 3: Select clusters
                    if self.verbose:
                        self.console.print("\n[yellow]🗂️  Selecting clusters...[/yellow]")
                    
                    selected_clusters = self._gemma_select_clusters_for_subtask(subtask)
                    
                    # Load tools from selected clusters (with sliding window)
                    if self.cluster_history:
                        # Combine with previous clusters
                        all_clusters = set(selected_clusters)
                        for prev_clusters in self.cluster_history[-self.cluster_window_size:]:
                            all_clusters.update(prev_clusters)
                        relevant_tools_list = self.cluster_manager.get_tools_by_clusters(list(all_clusters))
                        
                        if self.verbose:
                            self.console.print(f"[dim]   (Sliding window includes: {', '.join(sorted(all_clusters))})[/dim]")
                    else:
                        relevant_tools_list = self.cluster_manager.get_tools_by_clusters(selected_clusters)
                    
                    # Convert list to dict {name -> tool}
                    relevant_tools = {tool.name: tool for tool in relevant_tools_list}
                    
                    # Update cluster history
                    self.cluster_history.append(set(selected_clusters))
                    if len(self.cluster_history) > self.cluster_window_size:
                        self.cluster_history.pop(0)
                    
                    # Register tools with Qwen
                    self.qwen_agent.clear_tools()
                    for tool_instance in relevant_tools_list:
                        self.qwen_agent.register_tool(tool_instance)
                    
                    if self.verbose:
                        self.console.print(f"[dim]   Loaded {len(relevant_tools)} tools[/dim]")
                    
                    # Step 4a: Discover page structure if we're on a web page
                    if "find_elements" in [t.name for t in relevant_tools_list] and self.shared_context.get("current_url"):
                        if self.verbose:
                            self.console.print("\n[yellow]🔍 Discovering page structure...[/yellow]")
                        
                        # Discover different element types with specific selectors
                        structure = {"forms": [], "links_count": 0, "buttons": []}
                        discovery_context = self._build_qwen_context()
                        
                        try:
                            # Discover input fields (forms)
                            input_result = self.qwen_agent.query(
                                "Find all input elements on the page using selector_type='tag_name' and selector_value='input'",
                                context=discovery_context
                            )
                            if "found" in input_result.lower() or "input" in input_result.lower():
                                self._parse_inputs_into_structure(input_result, structure)
                            
                            # Discover links
                            link_result = self.qwen_agent.query(
                                "Find all link elements on the page using selector_type='tag_name' and selector_value='a'",
                                context=discovery_context
                            )
                            if "found" in link_result.lower() or "link" in link_result.lower():
                                self._parse_links_into_structure(link_result, structure)
                            
                            # Store discovered structure
                            self.shared_context["page_structure"] = structure
                            
                            if self.verbose:
                                if structure["forms"]:
                                    self.console.print(f"[dim]   Forms: {len(structure['forms'])} with inputs: {structure['forms'][0].get('inputs', [])[:3]}[/dim]")
                                if structure["links_count"] > 0:
                                    self.console.print(f"[dim]   Links: {structure['links_count']} available[/dim]")
                        except Exception as e:
                            if self.verbose:
                                self.console.print(f"[dim]   Discovery failed: {str(e)[:100]}[/dim]")
                    
                    # Step 4b: Gemma formulates instruction with structure knowledge
                    if self.verbose:
                        self.console.print("\n[yellow]💭 Formulating instruction...[/yellow]")
                    
                    instruction = self._gemma_formulate_instruction(subtask, relevant_tools)
                    
                    if self.verbose:
                        self.console.print(f"[green]📤 Instruction:[/green] {instruction}")
                    
                    # Step 5: Qwen executes
                    if self.verbose:
                        self.console.print("\n[yellow]🤖 Qwen executing...[/yellow]")
                    
                    # BEST PRACTICE: Set executor temperature low for deterministic tool use
                    original_temp = self.qwen_agent.temperature
                    self.qwen_agent.temperature = self.executor_temperature
                    
                    # Build message with context
                    context = self._build_qwen_context()
                    full_message = f"{context}\n\nInstruction: {instruction}"
                    agent_response = self.qwen_agent.query(full_message)
                    
                    # Restore original temperature
                    self.qwen_agent.temperature = original_temp
                    
                    if self.verbose:
                        self.console.print(Panel(
                            agent_response,
                            title="✓ Response",
                            border_style="green"
                        ))
                    
                    # CRÍTICO: ATUALIZAR CONTEXTO IMEDIATAMENTE após execução do Qwen
                    # Antes de qualquer avaliação ou detecção de loop
                    try:
                        from tools.browser_tools import BrowserSession
                        if BrowserSession._driver:
                            driver = BrowserSession._driver
                            if driver.current_url not in ["data:,", "about:blank"]:
                                if driver.current_url != self.shared_context["current_url"]:
                                    if self.shared_context["current_url"]:
                                        self.shared_context["visited_pages"].append(self.shared_context["current_url"])
                                    self.shared_context["current_url"] = driver.current_url
                                    self.shared_context["current_page_title"] = driver.title
                                    if self.verbose:
                                        self.console.print(f"[dim]🔄 Context updated: {driver.current_url}[/dim]")
                    except Exception as e:
                        if self.verbose:
                            self.console.print(f"[dim]⚠️  Context update failed: {e}[/dim]")
                    
                    # Atualizar contexto compartilhado com resultado
                    self._update_shared_context(instruction, agent_response)
                    
                    # DETECÇÃO AUTOMÁTICA DE LOOPS E TRAVAMENTOS
                    loop_detected = self._detect_loop_or_stuck(instruction, agent_response)
                    
                    if loop_detected:
                        if self.verbose:
                            self.console.print("[red]🚨 LOOP DETECTED! System forcing escalation...[/red]")
                        
                        # PASSO 1: Consultar Gemma Juiz para análise externa
                        if self.verbose:
                            self.console.print("[cyan]👨‍⚖️  Consulting Gemma Judge for external analysis...[/cyan]")
                        
                        judge_verdict = self._gemma_judge_situation(
                            task_description=task["description"],
                            subtasks=task["subtasks"],
                            current_subtask=subtask,
                            actions_taken=self.loop_detector["last_actions"],
                            browser_state=self._get_context_summary()
                        )
                        
                        if self.verbose:
                            self.console.print(f"[cyan]📋 Judge's verdict:[/cyan]\n{judge_verdict[:300]}...")
                        
                        # PASSO 2: Usar veredito do juiz + MOSTRAR subtasks que falharam
                        error_context = self._build_error_context(level="loop")
                        
                        # ADICIONAR lista de subtasks que FALHARAM
                        failed_subtasks_list = "\n".join([f"❌ {s}" for s in task["subtasks"][:subtask_index+1]])
                        error_context = f"{error_context}\n\nFAILED SUBTASKS (DO NOT REPEAT THESE):\n{failed_subtasks_list}\n\nEXTERNAL JUDGE ANALYSIS:\n{judge_verdict}"
                        
                        escalation_decision = {
                            "action": "revise_subtasks",
                            "error_context": error_context
                        }
                        
                        if self.verbose:
                            self.console.print("[yellow]⬆️  FORCED ESCALATION: Gemma revising subtasks[/yellow]")
                        
                        # Passar subtasks antigas para validação
                        old_subtasks = task["subtasks"].copy()
                        new_subtasks = self._gemma_revise_subtasks(
                            task_description=task["description"],
                            error_context=escalation_decision["error_context"],
                            old_subtasks=old_subtasks
                        )
                        
                        # VALIDAR: Novas subtasks são realmente diferentes?
                        if self._subtasks_too_similar(old_subtasks, new_subtasks):
                            if self.verbose:
                                self.console.print("[red]❌ REVISION REJECTED: New subtasks are too similar to failed ones[/red]")
                                self.console.print("[yellow]⬆️  ESCALATING TO TASK LEVEL[/yellow]")
                            # Escalar para revisão da task inteira
                            task["description"] = self._gemma_revise_task(task["description"], escalation_decision["error_context"])
                            task["subtasks"] = self._gemma_create_subtasks(task["description"])
                        else:
                            task["subtasks"] = new_subtasks
                        
                        subtask_index = 0
                        retry_count = 0
                        # Limpar detector de loop
                        self.loop_detector["last_actions"] = []
                        self.loop_detector["identical_action_count"] = 0
                        self.loop_detector["precondition_failures"] = 0
                        continue
                    
                    # Save to history
                    self.conversation_history.append({
                        "iteration": iteration_count,
                        "query": instruction,
                        "response": agent_response
                    })
                    
                    # Step 6: Gemma evaluates result
                    if self.verbose:
                        self.console.print("\n[yellow]🔍 Evaluating result...[/yellow]")
                    
                    evaluation = self._gemma_evaluate_result(subtask, instruction, agent_response)
                    
                    if self.verbose:
                        status_color = "green" if evaluation["completed"] else "red"
                        self.console.print(f"[{status_color}]Result:[/{status_color}] {'✅ Completed' if evaluation['completed'] else '❌ Not completed'}")
                        self.console.print(f"[dim]   Reasoning: {evaluation['reasoning']}[/dim]")
                        self.console.print(f"[dim]   Next action: {evaluation['next_action']}[/dim]")
                    
                    if evaluation["completed"] or evaluation["next_action"] == "next_subtask":
                        subtask_completed = True
                    elif evaluation["next_action"] == "retry":
                        retry_count += 1
                        if self.verbose:
                            self.console.print(f"[yellow]🔄 Retrying with feedback... (attempt {retry_count + 1}/{max_retries})[/yellow]")
                        
                        # Adicionar feedback explícito ao contexto do Qwen
                        error_feedback = f"""
FEEDBACK: Previous attempt failed.
Reason: {evaluation['reasoning']}
What went wrong: {agent_response[:200]}
Try a DIFFERENT approach or tool."""
                        
                        self.conversation_history.append({
                            "iteration": iteration_count,
                            "query": "SYSTEM_FEEDBACK",
                            "response": error_feedback
                        })
                        
                    elif evaluation["next_action"] == "reformulate":
                        # Will reformulate instruction in next iteration
                        retry_count += 1
                        if self.verbose:
                            self.console.print(f"[yellow]🔄 Reformulating approach... (attempt {retry_count + 1}/{max_retries})[/yellow]")
                        
                        # RASTREAR ERRO PARA ESCALAÇÃO
                        self._track_subtask_error(subtask, agent_response, evaluation["reasoning"])
                
                if not subtask_completed:
                    if self.verbose:
                        self.console.print("[red]⚠️  Subtask failed after max retries[/red]")
                    
                    # DECIDIR ESCALAÇÃO: subtask falhou, o que fazer?
                    escalation_decision = self._decide_escalation(subtask, task["description"])
                    
                    if escalation_decision["action"] == "revise_subtasks":
                        if self.verbose:
                            self.console.print("[yellow]⬆️  Escalating to Gemma: Revising subtasks for this task[/yellow]")
                        # Gemma recria subtasks com contexto de erros
                        task["subtasks"] = self._gemma_revise_subtasks(task["description"], escalation_decision["error_context"])
                        subtask_index = 0  # Recomeçar do início
                        continue
                    
                    elif escalation_decision["action"] == "revise_task":
                        if self.verbose:
                            self.console.print("[yellow]⬆️⬆️  Escalating to Gemma: Revising entire task[/yellow]")
                        # Gemma reformula a task inteira
                        task["description"] = self._gemma_revise_task(task["description"], escalation_decision["error_context"])
                        task["subtasks"] = self._gemma_create_subtasks(task["description"])
                        subtask_index = 0
                        continue
                    
                    elif escalation_decision["action"] == "skip_and_continue":
                        if self.verbose:
                            self.console.print("[yellow]➡️  Skipping failed subtask, continuing with next[/yellow]")
            
            # Validate if task objective was actually achieved
            task_achieved = self._validate_task_objective(task["description"])
            
            if task_achieved:
                self._update_task_status(task_id, "done")
                
                # BEST PRACTICE: Skill Harvesting - Registrar padrão bem-sucedido
                task_type = self._extract_task_type(task["description"])
                completed_actions = [st for st in task["subtasks"]]
                self._record_successful_pattern(task_type, completed_actions)
                
                if self.verbose:
                    self.console.print(f"\n[green]✅ Task {task_id} completed![/green]")
                    self.console.print(f"[dim]💾 Pattern '{task_type}' saved for reuse[/dim]")
            else:
                self._update_task_status(task_id, "failed")
                if self.verbose:
                    self.console.print(f"\n[red]❌ Task {task_id} FAILED - objective not achieved[/red]")
        
        # =====================================================================
        # FINAL: Compile answer
        # =====================================================================
        if self.verbose:
            self.console.print(f"\n[bold magenta]{'='*60}[/bold magenta]")
            self.console.print("[bold magenta]📊 Compiling final answer...[/bold magenta]")
            self.console.print(f"[bold magenta]{'='*60}[/bold magenta]\n")
        
        # Extract final answer from conversation history and shared context
        final_answer = f"Completed {len(self.todo_list['tasks'])} tasks:\n\n"
        
        for task in self.todo_list["tasks"]:
            final_answer += f"✅ {task['description']}\n"
        
        if self.shared_context["extracted_data"]:
            final_answer += "\n📦 Extracted data:\n"
            for url, data_list in self.shared_context["extracted_data"].items():
                final_answer += f"\nFrom {url}:\n"
                for data in data_list:
                    final_answer += f"  - {data}\n"
        
        return final_answer
    
    def query(self, user_query: str) -> str:
        """
        Processa uma query do usuário usando seleção de clusters
        
        Args:
            user_query: Pergunta/tarefa do usuário
            
        Returns:
            Resposta final
        """
        self.conversation_history = []
        
        # Inicializar TODO list com o objetivo
        self._initialize_todo_list(user_query)
        
        if self.verbose:
            self.console.print(Panel.fit(
                f"[bold cyan]🎯 USER QUERY[/bold cyan]\n\n{user_query}",
                border_style="cyan"
            ))
        
        # PASSO 1: Seleciona clusters
        if self.verbose:
            self.console.print("\n[bold magenta]🗂️  CLUSTER SELECTION[/bold magenta]")
        
        cluster_selection = self._call_gemma_cluster_selection(user_query)
        selected_clusters = cluster_selection["clusters"]
        reasoning = cluster_selection["reasoning"]
        
        if self.verbose:
            self.console.print(f"[cyan]Selected Clusters:[/cyan] {', '.join(selected_clusters)}")
            self.console.print(f"[dim]Reasoning: {reasoning}[/dim]")
        
        # PASSO 2: Carrega tools com SLIDING WINDOW
        # Adiciona clusters atuais ao histórico
        self.cluster_history.append(set(selected_clusters))
        
        # Manter apenas últimos N conjuntos
        if len(self.cluster_history) > self.cluster_window_size:
            self.cluster_history.pop(0)
        
        # Combinar clusters do sliding window
        all_clusters_in_window = set()
        for cluster_set in self.cluster_history:
            all_clusters_in_window.update(cluster_set)
        
        relevant_tools = self.cluster_manager.get_tools_by_clusters(list(all_clusters_in_window))
        
        if self.verbose:
            if len(self.cluster_history) > 1:
                self.console.print(f"[cyan]🔄 Tool sliding window:[/cyan] {len(all_clusters_in_window)} clusters total")
                self.console.print(f"[dim]Current: {', '.join(selected_clusters)} + Previous clusters[/dim]")
            self.console.print(f"[green]✓ Loaded {len(relevant_tools)} tools from {len(all_clusters_in_window)} clusters[/green]")
            self.console.print(f"[dim]Tools: {', '.join([t.name for t in relevant_tools])}[/dim]\n")
        
        # PASSO 3: Salva tools originais
        original_tools = self.qwen_agent.tools.copy()
        
        # PASSO 4: Loop iterativo com reavaliação de clusters
        for iteration in range(1, self.max_iterations + 1):
            if self.verbose:
                self.console.print(f"\n{'='*60}")
                self.console.print(f"[bold yellow]ITERATION {iteration}/{self.max_iterations}[/bold yellow]")
                self.console.print(f"{'='*60}\n")
            
            # A CADA ITERAÇÃO: Reavaliar clusters necessários
            if iteration > 1:
                if self.verbose:
                    self.console.print("[bold magenta]🔄 REAVALIAR CLUSTERS[/bold magenta]")
                
                cluster_selection = self._call_gemma_cluster_selection(user_query, consider_history=True)
                new_clusters = cluster_selection["clusters"]
                
                # Se mudou clusters, atualizar sliding window
                if set(new_clusters) != set(selected_clusters):
                    selected_clusters = new_clusters
                    
                    # Adicionar ao histórico de clusters
                    self.cluster_history.append(set(new_clusters))
                    if len(self.cluster_history) > self.cluster_window_size:
                        self.cluster_history.pop(0)
                    
                    # Combinar todos clusters no window
                    all_clusters_in_window = set()
                    for cluster_set in self.cluster_history:
                        all_clusters_in_window.update(cluster_set)
                    
                    relevant_tools = self.cluster_manager.get_tools_by_clusters(list(all_clusters_in_window))
                    
                    if self.verbose:
                        self.console.print(f"[yellow]⚡ Clusters changed:[/yellow] {', '.join(selected_clusters)}")
                        self.console.print(f"[cyan]🔄 Sliding window keeps:[/cyan] {', '.join(all_clusters_in_window)}")
                        self.console.print(f"[green]✓ Loaded {len(relevant_tools)} tools total[/green]")
                        self.console.print(f"[dim]Tools: {', '.join([t.name for t in relevant_tools])}[/dim]\n")
                    
                    # FIX: Use clear_tools() to properly reset both tools dict and schemas
                    self.qwen_agent.clear_tools()
                    for tool in relevant_tools:
                        self.qwen_agent.register_tool(tool)
                else:
                    # OPTIMIZATION: Same clusters, skip re-registration
                    if self.verbose:
                        self.console.print(f"[dim]✓ Same clusters: {', '.join(selected_clusters)} (skipping reload)[/dim]\n")
            else:
                # Primeira iteração: carregar tools iniciais
                # FIX: Use clear_tools() to ensure clean state
                self.qwen_agent.clear_tools()
                for tool in relevant_tools:
                    self.qwen_agent.register_tool(tool)
            
            # Gemma decide próxima ação
            decision = self._call_gemma_decision(user_query, selected_clusters)
            
            action = decision.get("action", "complete")
            reasoning = decision.get("reasoning", "")
            
            if self.verbose:
                self.console.print(f"[bold]🧠 GEMMA DECISION[/bold]")
                self.console.print(f"[cyan]Action:[/cyan] {action}")
                self.console.print(f"[dim]Reasoning: {reasoning}[/dim]\n")
            
            if action == "complete":
                final_answer = decision.get("final_answer", "Task completed")
                
                if self.verbose:
                    self.console.print(Panel.fit(
                        f"[bold green]✅ FINAL ANSWER[/bold green]\n\n{final_answer}",
                        border_style="green"
                    ))
                
                # FIX: Restore tools properly
                self.qwen_agent.clear_tools()
                for tool in original_tools.values():
                    self.qwen_agent.register_tool(tool)
                
                return final_answer
            
            # Executa query no agente
            query_for_agent = decision.get("query_for_agent", "")
            
            if self.verbose:
                self.console.print(f"[bold]🤖 QWEN AGENT[/bold]")
                self.console.print(f"[yellow]Query:[/yellow] {query_for_agent}\n")
            
            try:
                # Passar contexto completo para o Qwen: estado do navegador + sliding window das conversas
                context_for_qwen = self._build_qwen_context()
                agent_response = self.qwen_agent.query(query_for_agent, context=context_for_qwen)
                
                if self.verbose:
                    self.console.print(f"[green]✓ Response:[/green]")
                    self.console.print(Panel(agent_response, border_style="green"))
                
                # ATUALIZAR CONTEXTO COMPARTILHADO baseado na resposta
                self._update_shared_context(query_for_agent, agent_response)
                
                # Adiciona ao histórico
                self.conversation_history.append({
                    "iteration": iteration,
                    "query": query_for_agent,
                    "response": agent_response
                })
                
            except Exception as e:
                if self.verbose:
                    self.console.print(f"[red]✗ Error: {e}[/red]")
                
                self.conversation_history.append({
                    "iteration": iteration,
                    "query": query_for_agent,
                    "response": f"Error: {e}"
                })
        
        # Máximo de iterações atingido
        if self.verbose:
            self.console.print("[yellow]⚠ Maximum iterations reached[/yellow]")
        
        # FIX: Restore tools properly by re-registering instead of dict assignment
        self.qwen_agent.clear_tools()
        for tool in original_tools.values():
            self.qwen_agent.register_tool(tool)
        
        return "Maximum iterations reached. Task may be incomplete."
    
    def _update_shared_context(self, query: str, response: str):
        """
        Atualiza contexto compartilhado baseado na ação executada.
        Extrai estado do navegador e dados importantes.
        """
        response_lower = response.lower()
        
        # Atualizar URL atual se navegou
        if "opened" in response_lower or "now at:" in response_lower:
            import re
            urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', response)
            if urls:
                new_url = urls[-1]  # Pega última URL (a atual)
                if new_url != self.shared_context["current_url"]:
                    if self.shared_context["current_url"]:
                        self.shared_context["visited_pages"].append(self.shared_context["current_url"])
                    self.shared_context["current_url"] = new_url
        
        # Atualizar título da página
        if "page title:" in response_lower:
            import re
            match = re.search(r"page title:\s*['\"]([^'\"]+)['\"]", response, re.IGNORECASE)
            if match:
                self.shared_context["current_page_title"] = match.group(1)
        
        # Armazenar dados extraídos com key específica
        if "content:" in response_lower or "result:" in response_lower:
            url = self.shared_context["current_url"]
            if url:
                if url not in self.shared_context["extracted_data"]:
                    self.shared_context["extracted_data"][url] = []
                self.shared_context["extracted_data"][url].append(response[:500])  # Primeiros 500 chars
        
        # Registrar última ação
        self.shared_context["last_action"] = query
    
    def _get_context_summary(self) -> str:
        """
        Gera resumo do contexto compartilhado para incluir nos prompts.
        """
        lines = []
        
        # Verificar estado do browser primeiro (sem inicializar!)
        try:
            from tools.browser_tools import BrowserSession
            # Só verificar se já existe, não criar
            if BrowserSession._driver:
                driver = BrowserSession._driver
                if driver.current_url in ["data:,", "about:blank"]:
                    lines.append("⚠️  BROWSER IS EMPTY - No page loaded. Use open_url to navigate to a website.")
            else:
                lines.append("⚠️  BROWSER NOT STARTED - No browser session. Use open_url to start browser and navigate.")
        except:
            lines.append("⚠️  BROWSER NOT AVAILABLE")
        
        if self.shared_context["current_url"]:
            lines.append(f"📍 Current page: {self.shared_context['current_url']}")
        
        if self.shared_context["current_page_title"]:
            lines.append(f"📄 Page title: {self.shared_context['current_page_title']}")
        
        # Add page structure information if available
        if "page_structure" in self.shared_context and self.shared_context["page_structure"]:
            structure = self.shared_context["page_structure"]
            lines.append("\n📋 PAGE STRUCTURE:")
            if structure.get("forms"):
                lines.append(f"  • Forms: {len(structure['forms'])} found")
                for form in structure["forms"][:3]:  # Show first 3
                    lines.append(f"    - Inputs: {', '.join(form.get('inputs', [])[:5])}")
            if structure.get("links_count"):
                lines.append(f"  • Links: {structure['links_count']} available")
            if structure.get("buttons"):
                lines.append(f"  • Buttons: {', '.join(structure['buttons'][:5])}")
        
        if self.shared_context["visited_pages"]:
            lines.append(f"🔙 Previously visited: {len(self.shared_context['visited_pages'])} pages")
        
        if self.shared_context["extracted_data"]:
            lines.append(f"📦 Data extracted from {len(self.shared_context['extracted_data'])} pages")
        
        if self.shared_context["last_action"]:
            lines.append(f"⚡ Last action: {self.shared_context['last_action'][:80]}...")
        
        return "\n".join(lines) if lines else "No browser state yet"
    
    def _build_qwen_context(self, window_size: int = 3) -> str:
        """
        Constrói contexto completo para o Qwen com sliding window das conversas.
        IMPORTANTE: Inclui dados determinísticos (links, elementos) automaticamente
        para evitar que o modelo precise "descobrir" o que já sabemos.
        
        Args:
            window_size: Número de interações recentes a incluir
            
        Returns:
            String com contexto formatado
        """
        sections = []
        
        # 1. TODO LIST - saber o que está sendo feito
        todo_summary = self._get_todo_summary()
        sections.append(f"CURRENT PLAN:\n{todo_summary}")
        
        # 2. Estado do navegador
        browser_state = self._get_context_summary()
        sections.append(f"BROWSER STATE:\n{browser_state}")
        
        # 3. DADOS DETERMINÍSTICOS - Links e elementos já descobertos
        page_data = self._get_page_data_for_qwen()
        if page_data:
            sections.append(f"PAGE DATA (already extracted):\n{page_data}")
        
        # 4. Sliding window das últimas conversas
        if self.conversation_history:
            recent = self.conversation_history[-window_size:]
            conv_lines = []
            for h in recent:
                conv_lines.append(f"Turn {h['iteration']}:")
                conv_lines.append(f"  Instruction: {h['query']}")
                conv_lines.append(f"  Your response: {h['response'][:200]}...")
            
            sections.append(f"RECENT CONVERSATION:\n" + "\n".join(conv_lines))
        
        return "\n\n".join(sections)
    
    def _record_successful_pattern(self, task_type: str, actions: List[str]):
        """
        BEST PRACTICE: Skill Harvesting - Registra padrões de ações bem-sucedidas.
        Inspirado no Agent-E que memoriza sequências de navegação efetivas.
        
        Args:
            task_type: Tipo de tarefa (ex: "google_search", "form_fill")
            actions: Lista de ações que levaram ao sucesso
        """
        # Procura padrão existente
        for pattern in self.successful_patterns:
            if pattern["type"] == task_type:
                pattern["examples"].append(actions)
                pattern["count"] += 1
                return
        
        # Novo padrão
        self.successful_patterns.append({
            "type": task_type,
            "examples": [actions],
            "count": 1
        })
        
        # Manter apenas os 10 padrões mais usados
        if len(self.successful_patterns) > 10:
            self.successful_patterns.sort(key=lambda x: x["count"], reverse=True)
            self.successful_patterns = self.successful_patterns[:10]
    
    def _get_similar_pattern(self, task_description: str) -> Optional[List[str]]:
        """
        Busca padrão similar registrado para reutilizar.
        
        Args:
            task_description: Descrição da tarefa atual
            
        Returns:
            Lista de ações sugeridas ou None
        """
        task_lower = task_description.lower()
        
        # Busca por palavras-chave
        for pattern in self.successful_patterns:
            if pattern["type"].lower() in task_lower or any(kw in task_lower for kw in pattern["type"].split("_")):
                if pattern["examples"]:
                    return pattern["examples"][-1]  # Retorna exemplo mais recente
        
        return None
    
    def _extract_task_type(self, task_description: str) -> str:
        """
        Extrai tipo de tarefa para categorização de padrões.
        
        Args:
            task_description: Descrição da tarefa
            
        Returns:
            String identificando tipo (ex: "web_search", "form_fill", "data_extract")
        """
        task_lower = task_description.lower()
        
        # Mapeamento de keywords para tipos
        task_types = {
            "search": "web_search",
            "google": "web_search",
            "find": "web_search",
            "look for": "web_search",
            "form": "form_fill",
            "fill": "form_fill",
            "submit": "form_fill",
            "login": "form_login",
            "extract": "data_extract",
            "scrape": "data_extract",
            "get data": "data_extract",
            "click": "web_navigation",
            "navigate": "web_navigation",
            "open": "web_navigation",
            "calculate": "math_operation",
            "compute": "math_operation"
        }
        
        for keyword, task_type in task_types.items():
            if keyword in task_lower:
                return task_type
        
        return "general_task"
    
    def _get_page_data_for_qwen(self) -> str:
        """
        Extrai dados determinísticos da página atual automaticamente.
        Isso evita que o Qwen precise "descobrir" informações que o Selenium já tem.
        
        IMPORTANTE: Mostra estatísticas e amostras, deixando claro quando há mais dados.
        
        Returns:
            String formatada com links, elementos, etc. ou vazio se não estiver em página web
        """
        try:
            from tools.browser_tools import BrowserSession
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Só verificar se driver já existe, não inicializar
            if not BrowserSession._driver:
                return ""
            
            driver = BrowserSession._driver
            
            # Se browser está vazio, informar explicitamente
            if driver.current_url in ["data:,", "about:blank"]:
                return "⚠️  BROWSER IS EMPTY - No page loaded yet. You need to open_url first before extracting links or interacting with page elements."
            
            data_lines = []
            
            # BEST PRACTICE: DOM Distillation - Filtrar apenas elementos interativos relevantes
            # Inspirado no Agent-E que reduziu DOM para melhorar performance
            try:
                from selenium.webdriver.common.by import By
                
                # Esperar links estarem disponíveis
                try:
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.TAG_NAME, "a"))
                    )
                except:
                    pass  # Continue mesmo se não encontrar links
                
                all_links = driver.find_elements(By.TAG_NAME, "a")
                    
                # DOM DISTILLATION: Filtrar apenas links válidos e interativos
                valid_links = []
                for idx, link in enumerate(all_links):
                    try:
                        # Pular elementos ocultos ou não interativos
                        if not link.is_displayed() or not link.is_enabled():
                            continue
                        
                        text = link.text.strip()
                        href = link.get_attribute("href")
                        
                        # Filtros: texto presente, href válido, não navegação JS
                        if text and href and not href.startswith(("javascript:", "#", "mailto:")):
                            # Pular links de navegação/footer genéricos
                            if text.lower() in ["home", "back", "next", "previous", "close"]:
                                continue
                                
                        valid_links.append((idx, text, href))
                    except:
                        continue  # Skip stale elements
                
                if valid_links:
                    total = len(valid_links)
                    showing = min(10, total)
                    
                    data_lines.append(f"📊 LINKS: Found {total} clickable links on page (showing top {showing})")
                    
                    for idx, text, href in valid_links[:showing]:
                        data_lines.append(f"  [{idx}] {text[:60]} → {href[:80]}")
                    
                    if total > showing:
                        remaining = total - showing
                        data_lines.append(f"\n  ⚠️  {remaining} more links available!")
                        data_lines.append(f"  💡 Use extract_links(filter_text='keyword') to find specific links")
            except:
                pass
            
            # Formulários disponíveis - mostrar estatísticas
            try:
                inputs = driver.find_elements(By.TAG_NAME, "input")
                textareas = driver.find_elements(By.TAG_NAME, "textarea")
                selects = driver.find_elements(By.TAG_NAME, "select")
                
                total_inputs = len(inputs) + len(textareas) + len(selects)
                
                if total_inputs > 0:
                    data_lines.append(f"\n📊 FORM INPUTS: Found {total_inputs} input fields")
                    
                    form_info = []
                    # Inputs de texto
                    for inp in inputs[:5]:
                        try:
                            name = inp.get_attribute("name")
                            inp_type = inp.get_attribute("type") or "text"
                            placeholder = inp.get_attribute("placeholder") or ""
                            if name:
                                info = f"  - '{name}' (type: {inp_type})"
                                if placeholder:
                                    info += f" [placeholder: {placeholder[:30]}]"
                                form_info.append(info)
                        except:
                            continue
                    
                    # Textareas
                    for ta in textareas[:2]:
                        try:
                            name = ta.get_attribute("name")
                            if name:
                                form_info.append(f"  - '{name}' (type: textarea)")
                        except:
                            continue
                    
                    if form_info:
                        data_lines.extend(form_info)
                    
                    if total_inputs > len(form_info):
                        data_lines.append(f"  ⚠️  {total_inputs - len(form_info)} more inputs not shown")
            except:
                pass
            
            # Botões clicáveis
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                submit_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
                
                total_buttons = len(buttons) + len(submit_inputs)
                
                if total_buttons > 0:
                    data_lines.append(f"\n📊 BUTTONS: Found {total_buttons} clickable buttons")
                    
                    button_info = []
                    for btn in buttons[:3]:
                        try:
                            text = btn.text.strip() or btn.get_attribute("value") or "unnamed"
                            button_info.append(f"  - Button: '{text[:40]}'")
                        except:
                            continue
                    
                    if button_info:
                        data_lines.extend(button_info)
                    
                    if total_buttons > 3:
                        data_lines.append(f"  ⚠️  {total_buttons - 3} more buttons available")
            except:
                pass
            
            return "\n".join(data_lines) if data_lines else ""
            
        except Exception as e:
            return ""
    
    def _initialize_todo_list(self, main_goal: str):
        """
        Inicializa TODO list baseado no objetivo principal.
        Gemma vai decompor em tarefas no primeiro ciclo.
        """
        self.todo_list = {
            "main_goal": main_goal,
            "tasks": []
        }
        self.task_counter = 0
    
    def _add_task(self, description: str, subtasks: list = None) -> int:
        """
        Adiciona uma tarefa à TODO list.
        
        Args:
            description: Descrição da tarefa
            subtasks: Lista de subtarefas (opcional)
            
        Returns:
            ID da tarefa criada
        """
        self.task_counter += 1
        task = {
            "id": self.task_counter,
            "description": description,
            "status": "pending",
            "subtasks": subtasks or []
        }
        self.todo_list["tasks"].append(task)
        return self.task_counter
    
    def _update_task_status(self, task_id: int, status: str):
        """
        Atualiza status de uma tarefa.
        
        Args:
            task_id: ID da tarefa
            status: Novo status (pending, in_progress, done)
        """
        for task in self.todo_list["tasks"]:
            if task["id"] == task_id:
                task["status"] = status
                break
    
    def _get_todo_summary(self) -> str:
        """
        Gera resumo formatado do TODO list para system prompts.
        """
        if not self.todo_list["tasks"]:
            return "No tasks defined yet"
        
        lines = [f"🎯 MAIN GOAL: {self.todo_list['main_goal']}", ""]
        
        for task in self.todo_list["tasks"]:
            status_icon = "✅" if task["status"] == "done" else "🔄" if task["status"] == "in_progress" else "⬜"
            lines.append(f"{status_icon} Task {task['id']}: {task['description']} [{task['status'].upper()}]")
            
            if task["subtasks"]:
                for i, subtask in enumerate(task["subtasks"], 1):
                    lines.append(f"    {i}. {subtask}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # NEW WORKFLOW: Step-by-step task execution
    # =========================================================================
    
    def _gemma_create_todo(self, user_query: str) -> Dict[str, Any]:
        """
        STEP 1: Gemma analyzes user request and creates TODO list with main tasks.
        
        Args:
            user_query: User's original request
            
        Returns:
            Dict with main_goal and tasks list
        """
        system_prompt = """You are a project manager analyzing user requests.

Your job: Break down the user's request into 2-5 HIGH-LEVEL tasks (not detailed steps).

Example:
User: "Search Google for Python creator, find his birth year, calculate his age"
Tasks:
1. Navigate to Google and search for Python creator
2. Find creator's birth year from results
3. Calculate current age from birth year

Respond with JSON:
{
    "main_goal": "brief summary of user's goal",
    "tasks": [
        {"description": "high-level task 1"},
        {"description": "high-level task 2"}
    ]
}

Keep tasks high-level. Subtasks will be created later."""

        user_prompt = f"User request: {user_query}\n\nCreate the TODO list."
        
        response = self.gemma_client.chat.completions.create(
            model=self.gemma_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parsing robusto
        result, error = self._robust_json_parse(content)
        
        if result is None:
            if self.verbose:
                self.console.print(f"[yellow]⚠ JSON parse error: {error}. Creating simple TODO.[/yellow]")
            # Fallback: criar TODO simples
            return {
                "main_goal": user_query,
                "tasks": [
                    {"id": 1, "description": user_query, "status": "pending"}
                ]
            }
        
        return result
    
    def _gemma_create_subtasks(self, task_description: str, hint: Optional[List[str]] = None) -> List[str]:
        """
        STEP 2: Gemma breaks down a task into detailed subtasks.
        BEST PRACTICE: Usa skill harvesting hint se disponível.
        
        Args:
            task_description: Description of the main task
            hint: Optional list of similar successful actions to guide planning
            
        Returns:
            List of subtask descriptions
        """
        browser_state = self._get_context_summary()
        browser_not_started = "BROWSER NOT STARTED" in browser_state
        
        # Adicionar hint de padrão similar se disponível
        hint_text = ""
        if hint:
            hint_text = f"\n\nSIMILAR SUCCESSFUL PATTERN (use as inspiration):\n"
            hint_text += "\n".join(f"{i+1}. {action}" for i, action in enumerate(hint[:5]))
            hint_text += "\n\nYou can adapt this pattern to the current task."
        
        system_prompt = f"""Break this task into atomic subtasks. Each subtask = ONE tool call.

Task: {task_description}
Browser: {browser_state}{hint_text}

RULES:
1. If browser not started, FIRST subtask MUST be: "Open URL https://google.com"
2. Each subtask = exactly ONE action (never combine)
3. Logical order: navigate → extract → click → fill
4. Be specific: include exact search terms, link text, etc.

Respond with JSON:
{{
    "subtasks": ["subtask 1", "subtask 2"]
}}"""

        user_prompt = f"Task to break down: {task_description}"
        
        response = self.gemma_client.chat.completions.create(
            model=self.gemma_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        return result["subtasks"]
    
    def _gemma_select_clusters_for_subtask(self, subtask: str) -> List[str]:
        """
        STEP 3: Gemma selects appropriate cluster(s) for a specific subtask.
        
        Args:
            subtask: Description of the subtask
            
        Returns:
            List of cluster names
        """
        cluster_info = []
        for cluster_name in ClusterManager.get_cluster_names():
            description = ClusterManager.get_cluster_description(cluster_name)
            cluster_info.append(f"- {cluster_name}: {description}")
        
        clusters_text = "\n".join(cluster_info)
        
        system_prompt = f"""Select 1-2 clusters needed for this subtask.

CLUSTERS:
{clusters_text}

Subtask: {subtask}

Respond with JSON:
{{
    "clusters": ["CLUSTER1"],
    "reasoning": "brief reason"
}}"""

        user_prompt = f"Subtask: {subtask}\n\nWhich cluster(s) contain the tools needed?"
        
        response = self.gemma_client.chat.completions.create(
            model=self.gemma_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parsing robusto com fallback
        result, error = self._robust_json_parse(content)
        
        if result is None:
            if self.verbose:
                self.console.print(f"[yellow]⚠ JSON parse error: {error}. Using text fallback.[/yellow]")
            result = self._extract_fallback_from_text(content, ["clusters", "reasoning"])
        
        if self.verbose:
            self.console.print(f"[yellow]🗂️  Selected clusters: {', '.join(result.get('clusters', ['WEB']))}[/yellow]")
            self.console.print(f"[dim]   Reasoning: {result.get('reasoning', 'Extracted from text')}[/dim]")
        
        return result.get("clusters", ["WEB"])
    
    def _gemma_formulate_instruction(self, subtask: str, available_tools: Dict[str, Any]) -> str:
        """
        STEP 4: Gemma formulates specific instruction for Qwen based on available tools.
        
        Args:
            subtask: The subtask to accomplish
            available_tools: Dict of tool_name -> tool_object
            
        Returns:
            Specific instruction string for Qwen
        """
        # Build simple tool list
        tools_list = ", ".join(available_tools.keys())
        
        system_prompt = f"""Convert this subtask into a specific instruction for tool execution.

Subtask: {subtask}
Available tools: {tools_list}

Be specific:
- Include exact search terms from subtask
- Specify selectors (e.g., selector_type='name', selector_value='q')
- For links: extract first, then click by index

Respond with JSON:
{{
    "instruction": "specific instruction"
}}"""

        user_prompt = f"Formulate instruction for: {subtask}"
        
        response = self.gemma_client.chat.completions.create(
            model=self.gemma_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parsing robusto com fallback
        result, error = self._robust_json_parse(content)
        
        if result is None:
            if self.verbose:
                self.console.print(f"[yellow]⚠ JSON parse error: {error}. Using text as instruction.[/yellow]")
            result = self._extract_fallback_from_text(content, ["instruction"])
        
        # Safety check: ensure result is a dict
        if not isinstance(result, dict):
            if self.verbose:
                self.console.print(f"[yellow]⚠ Result is not a dict (got {type(result)}). Using subtask as instruction.[/yellow]")
            return subtask
        
        return result.get("instruction", subtask)
    
    def _gemma_evaluate_result(self, subtask: str, instruction: str, result: str) -> Dict[str, Any]:
        """
        STEP 5: Gemma evaluates if subtask was completed successfully.
        
        Args:
            subtask: The subtask that was attempted
            instruction: The instruction given to Qwen
            result: Qwen's execution result
            
        Returns:
            Dict with status and next_action
        """
        system_prompt = f"""Did this subtask complete?

Subtask: {subtask}
Result: {result[:200]}
Browser now: {self._get_context_summary()}

Check:
- URL changed? Content changed? Error message?
- If result says "success" but nothing changed → NOT completed

Respond with JSON:
{{
    "completed": true/false,
    "reasoning": "brief evidence",
    "next_action": "next_subtask" or "reformulate" or "retry"
}}"""

        user_prompt = f"Execution result:\n{result}\n\nDid the subtask ACTUALLY complete? Provide evidence from browser state."
        
        response = self.gemma_client.chat.completions.create(
            model=self.gemma_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parsing robusto com fallback
        result, error = self._robust_json_parse(content)
        
        if result is None:
            if self.verbose:
                self.console.print(f"[yellow]⚠ JSON parse error: {error}. Using text analysis.[/yellow]")
            result = self._extract_fallback_from_text(content, ["completed", "reasoning", "next_action"])
        
        return result
    
    def _validate_task_objective(self, task_description: str) -> bool:
        """
        Validates if the task objective was actually achieved based on browser state.
        
        Args:
            task_description: The main task that should have been completed
            
        Returns:
            True if objective achieved, False otherwise
        """
        system_prompt = f"""You are validating if a task objective was actually achieved.

TASK: {task_description}

CURRENT BROWSER STATE:
{self._get_context_summary()}

CHECK FOR CONCRETE EVIDENCE:
- For "open Google": URL must be google.com
- For "search for X": URL must show search results (e.g., /search?q=...)
- For "review results": Current page must have search results content
- For "navigate to X": URL must be at destination X

BE STRICT:
- If task was "search" but URL is still google.com homepage → FAILED
- If task was "review results" but no results visible → FAILED
- Only return true if browser state PROVES objective was achieved

Respond with JSON:
{{
    "achieved": true/false,
    "evidence": "concrete evidence from browser state"
}}"""

        user_prompt = "Was the task objective achieved? Provide evidence."
        
        try:
            response = self.gemma_client.chat.completions.create(
                model=self.gemma_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=150
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parsing robusto com fallback
            result, error = self._robust_json_parse(content)
            
            if result is None:
                if self.verbose:
                    self.console.print(f"[yellow]⚠ JSON parse error: {error}. Using text analysis.[/yellow]")
                result = self._extract_fallback_from_text(content, ["achieved", "evidence"])
            
            return result.get("achieved", False)
        except Exception as e:
            if self.verbose:
                self.console.print(f"[dim]Task validation error: {str(e)[:100]}[/dim]")
            return False
    
    def _parse_inputs_into_structure(self, discovery_result: str, structure: dict):
        """Parse input discovery result and update structure."""
        import re
        
        result_lower = discovery_result.lower()
        
        # Look for patterns like "found X elements" or "X inputs found"
        count_match = re.search(r"(\d+)\s*(?:elements?|inputs?)", result_lower)
        if count_match:
            count = int(count_match.group(1))
            if count > 0:
                # Try to extract input names
                inputs = re.findall(r"name=['\"]([^'\"]+)['\"]|name:\s*['\"]?([a-zA-Z_][a-zA-Z0-9_]*)", discovery_result, re.IGNORECASE)
                input_names = [i[0] or i[1] for i in inputs if i[0] or i[1]]
                
                if not input_names:
                    # Generic parsing - look for common input names
                    common_inputs = ["q", "search", "query", "email", "username", "password"]
                    for inp in common_inputs:
                        if inp in result_lower:
                            input_names.append(inp)
                
                if input_names:
                    structure["forms"].append({"inputs": input_names[:10]})
    
    def _parse_links_into_structure(self, discovery_result: str, structure: dict):
        """Parse link discovery result and update structure."""
        import re
        
        result_lower = discovery_result.lower()
        
        # Look for patterns like "found X elements" or "X links"
        count_match = re.search(r"(\d+)\s*(?:elements?|links?)", result_lower)
        if count_match:
            count = int(count_match.group(1))
            structure["links_count"] = count
# Métodos adicionais para escalação de erros
# Adicionar ao gemma_cluster_coordinator.py

    def _track_subtask_error(self, subtask: str, response: str, reasoning: str):
        """
        Rastreia erro de subtask para decidir escalação futura
        
        Args:
            subtask: Descrição da subtask que falhou
            response: Resposta do Qwen
            reasoning: Raciocínio do Gemma sobre por que falhou
        """
        # Procurar se já existe registro desta subtask
        existing = None
        for entry in self.error_tracking["subtask_failures"]:
            if entry["subtask"] == subtask:
                existing = entry
                break
        
        if existing:
            existing["attempts"] += 1
            existing["errors"].append({
                "response": response[:200],
                "reasoning": reasoning
            })
        else:
            self.error_tracking["subtask_failures"].append({
                "subtask": subtask,
                "attempts": 1,
                "errors": [{
                    "response": response[:200],
                    "reasoning": reasoning
                }]
            })
    
    def _decide_escalation(self, current_subtask: str, task_description: str) -> Dict[str, Any]:
        """
        Decide se deve escalar e para qual nível
        
        Returns:
            Dict com "action" e "error_context"
            Actions: "revise_subtasks", "revise_task", "skip_and_continue"
        """
        # Contar falhas da subtask atual
        current_failures = 0
        error_list = []
        for entry in self.error_tracking["subtask_failures"]:
            if entry["subtask"] == current_subtask:
                current_failures = entry["attempts"]
                error_list = entry["errors"]
                break
        
        # Total de falhas de subtasks na task atual
        total_subtask_failures = sum(e["attempts"] for e in self.error_tracking["subtask_failures"])
        
        # Decisão de escalação
        if current_failures >= self.SUBTASK_RETRY_LIMIT and self.error_tracking["task_revision_count"] < self.TASK_REVISION_LIMIT:
            # Muitas falhas numa subtask → revisar subtasks da task
            error_context = self._build_error_context(level="subtask")
            self.error_tracking["task_revision_count"] += 1
            self.error_tracking["last_escalation_level"] = "subtask"
            return {
                "action": "revise_subtasks",
                "error_context": error_context
            }
        
        elif self.error_tracking["task_revision_count"] >= self.TASK_REVISION_LIMIT:
            # Já revisamos subtasks demais → revisar task inteira
            error_context = self._build_error_context(level="task")
            self.error_tracking["todo_revision_count"] += 1
            self.error_tracking["last_escalation_level"] = "task"
            return {
                "action": "revise_task",
                "error_context": error_context
            }
        
        else:
            # Pular e continuar
            return {
                "action": "skip_and_continue",
                "error_context": ""
            }
    
    def _build_error_context(self, level: str) -> str:
        """
        Constrói contexto rico de erros para Gemma usar na revisão
        
        Args:
            level: "subtask", "task", "todo", ou "loop"
            
        Returns:
            String com histórico de erros formatado
        """
        lines = []
        
        # Contexto específico para detecção de loop
        if level == "loop":
            lines.append("🚨 LOOP DETECTED - System intervention required!")
            lines.append("")
            lines.append(f"Last {len(self.loop_detector['last_actions'])} actions: {self.loop_detector['last_actions']}")
            lines.append(f"Identical action count: {self.loop_detector['identical_action_count']}")
            lines.append(f"Precondition failures ignored: {self.loop_detector['precondition_failures']}")
            lines.append("")
            lines.append(f"Current browser state: {self._get_context_summary()}")
            lines.append("")
            lines.append("DIAGNOSIS: Qwen is stuck trying the same action repeatedly.")
            lines.append("The current subtasks are WRONG and need complete revision.")
            lines.append("")
            return "\n".join(lines)
        
        # Contexto geral de erros
        lines.append("ERROR HISTORY (learn from these failures):")
        lines.append("")
        
        for i, entry in enumerate(self.error_tracking["subtask_failures"], 1):
            lines.append(f"Failure {i}: '{entry['subtask']}'")
            lines.append(f"  Attempts: {entry['attempts']}")
            for j, err in enumerate(entry["errors"], 1):
                lines.append(f"  Attempt {j} reasoning: {err['reasoning']}")
            lines.append("")
        
        lines.append(f"Task revisions so far: {self.error_tracking['task_revision_count']}")
        lines.append(f"TODO revisions so far: {self.error_tracking['todo_revision_count']}")
        
        return "\n".join(lines)
    
    def _gemma_revise_subtasks(self, task_description: str, error_context: str, old_subtasks: List[str]) -> List[str]:
        """
        Gemma revisa subtasks baseado em erros anteriores
        
        Args:
            task_description: Descrição da task
            error_context: Contexto de erros acumulados
            old_subtasks: Lista de subtasks antigas que FALHARAM
            
        Returns:
            Nova lista de subtasks
        """
        browser_state = self._get_context_summary()
        
        # Extract judge verdict from error_context
        judge_verdict = ""
        if "EXTERNAL JUDGE ANALYSIS:" in error_context:
            judge_verdict = error_context.split("EXTERNAL JUDGE ANALYSIS:")[1].strip()
        
        browser_not_started = "BROWSER NOT STARTED" in browser_state
        
        system_prompt = f"""JUDGE'S DIAGNOSIS:
{judge_verdict[:300]}

Task: {task_description}
Browser: {browser_state}

OLD SUBTASKS (FAILED):
{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(old_subtasks[:3]))}

CREATE NEW SUBTASKS:
1. MUST be different from old ones
2. If browser not started, FIRST = "Open URL https://google.com"
3. Follow judge's recommendations
4. Each subtask = ONE tool call

Respond with JSON:
{{
    "subtasks": ["new subtask 1", "new subtask 2"]
}}"""

        user_prompt = f"Revise subtasks for: {task_description}"
        
        response = self.gemma_client.chat.completions.create(
            model=self.gemma_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        return result["subtasks"]
    
    def _subtasks_too_similar(self, old_subtasks: List[str], new_subtasks: List[str]) -> bool:
        """
        Verifica se novas subtasks são muito similares às antigas (indicando revisão inútil)
        
        Returns:
            True se new_subtasks são muito similares a old_subtasks
        """
        # Se primeiro subtask é idêntico, rejeitamos
        if new_subtasks and old_subtasks:
            if new_subtasks[0].lower().strip() == old_subtasks[0].lower().strip():
                return True
        
        # Se 70% ou mais das subtasks são idênticas, rejeitamos
        matches = 0
        for new_st in new_subtasks:
            new_clean = new_st.lower().strip()
            for old_st in old_subtasks:
                old_clean = old_st.lower().strip()
                if new_clean == old_clean or new_clean in old_clean or old_clean in new_clean:
                    matches += 1
                    break
        
        similarity_ratio = matches / max(len(new_subtasks), 1)
        return similarity_ratio >= 0.7
    
    def _gemma_revise_task(self, task_description: str, error_context: str) -> str:
        """
        Gemma revisa a task inteira baseado em falhas repetidas
        
        Returns:
            Nova descrição de task
        """
        system_prompt = f"""Task '{task_description}' failed even after retries.

{error_context[:200]}

Revise the task:
- Break into smaller pieces?
- Add missing prerequisites?
- Change approach?

Respond with JSON:
{{
    "revised_task": "simpler, achievable task"
}}"""

        response = self.gemma_client.chat.completions.create(
            model=self.gemma_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Revise: {task_description}"}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        content = response.choices[0].message.content.strip()
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        result = json.loads(content)
        return result.get("revised_task", task_description)

    def _detect_loop_or_stuck(self, instruction: str, response: str) -> bool:
        """
        Detecta automaticamente se o sistema está em loop ou travado
        
        Critérios:
        1. Mesma ação sendo repetida (ex: extract_links 3x seguidas)
        2. PRECONDITION FAILED sendo ignorado repetidamente
        3. Mesmo erro se repetindo
        
        Returns:
            True se detectou loop/travamento
        """
        # Extrair ação do response (tool calls)
        current_action = None
        try:
            # Tentar extrair tool call do JSON
            if "extract_links" in response:
                current_action = "extract_links"
            elif "open_url" in response:
                current_action = "open_url"
            elif "click_link_by_index" in response:
                current_action = "click_link_by_index"
            elif "fill_form" in response:
                current_action = "fill_form"
        except:
            pass
        
        # Adicionar à lista de últimas ações
        if current_action:
            self.loop_detector["last_actions"].append(current_action)
            # Manter apenas últimas 5
            if len(self.loop_detector["last_actions"]) > 5:
                self.loop_detector["last_actions"].pop(0)
        
        # DETECTOR 1: Mesma ação repetida múltiplas vezes
        if len(self.loop_detector["last_actions"]) >= 3:
            last_3 = self.loop_detector["last_actions"][-3:]
            if len(set(last_3)) == 1:  # Todas iguais
                self.loop_detector["identical_action_count"] += 1
                if self.loop_detector["identical_action_count"] >= self.IDENTICAL_ACTION_LIMIT:
                    return True  # LOOP DETECTADO!
        
        # DETECTOR 2: PRECONDITION FAILED sendo ignorado
        # A tool retorna erro de precondição mas Qwen continua tentando
        if "PRECONDITION FAILED" in response or "HINT:" in response:
            self.loop_detector["precondition_failures"] += 1
            if self.loop_detector["precondition_failures"] >= self.PRECONDITION_FAILURE_LIMIT:
                return True  # IGNORANDO HINTS!
        
        # DETECTOR 3: Browser não iniciado mas tentando usar
        browser_state = self._get_context_summary()
        if "BROWSER NOT STARTED" in browser_state and current_action and current_action != "open_url":
            # Está tentando fazer algo que não é open_url com browser não iniciado
            self.loop_detector["precondition_failures"] += 1
            if self.loop_detector["precondition_failures"] >= 1:  # Uma vez já basta
                return True
        
        return False

    def _gemma_judge_situation(
        self, 
        task_description: str,
        subtasks: List[str],
        current_subtask: str,
        actions_taken: List[str],
        browser_state: str
    ) -> str:
        """
        Gemma Juiz: Análise externa e imparcial da situação problemática
        
        Este é um SEGUNDO Gemma, separado, que atua como auditor externo.
        Ele analisa o que deu errado sem viés do planejador original.
        
        Args:
            task_description: Descrição da task
            subtasks: Lista de subtasks planejadas
            current_subtask: Subtask que está travada
            actions_taken: Ações que o Qwen tentou
            browser_state: Estado atual do browser
            
        Returns:
            Análise e diagnóstico do juiz
        """
        judge_prompt = f"""EXTERNAL JUDGE: Analyze this failure.

Task: {task_description}
Stuck on: {current_subtask}
Browser: {browser_state}

Recent attempts:
{chr(10).join(f"- {a}" for a in actions_taken[-3:])}

ANALYZE:
1. ROOT CAUSE: What's the fundamental problem?
2. WHY LOOPING: What's missing or wrong?
3. FIX: What should be the FIRST correct action?

Be brief and direct."""

        try:
            response = self.gemma_client.chat.completions.create(
                model=self.gemma_model,
                messages=[
                    {"role": "system", "content": "You are an expert debugging assistant analyzing automation failures."},
                    {"role": "user", "content": judge_prompt}
                ],
                temperature=0.2,  # Baixa temperatura para análise precisa
                max_tokens=400
            )
            
            verdict = response.choices[0].message.content.strip()
            return verdict
            
        except Exception as e:
            return f"Judge analysis failed: {str(e)}"
