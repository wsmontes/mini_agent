#!/usr/bin/env python3
"""
OutlinesQwenAgent - Enhanced QwenAgent with structured generation support.
Extends base QwenAgent with improved JSON parsing and optional Outlines integration.
"""

import json
import os
from typing import List, Dict, Any, Optional, Callable
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OutlinesQwenAgent:
    """
    Enhanced Qwen3-4B Agent with structured generation capabilities.
    
    Improvements over base QwenAgent:
    - Better JSON parsing with fallback strategies
    - Optional context parameter for contextual queries
    - More robust error handling
    - Support for structured generation (future: Outlines integration)
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.8,
        max_tokens: int = 2048,
        enable_thinking: bool = False,
        auto_execute_tools: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize the enhanced Qwen agent.
        
        Args:
            model_name: Model identifier (default from env)
            base_url: LM Studio API base URL (default from env)
            api_key: API key (default from env)
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            enable_thinking: Enable reasoning/thinking mode
            auto_execute_tools: Automatically execute tool calls
            verbose: Enable verbose logging
        """
        self.model_name = model_name or os.getenv("MODEL_NAME", "qwen3-4b-toolcall")
        self.base_url = base_url or os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
        self.api_key = api_key or os.getenv("LM_STUDIO_API_KEY", "lm-studio")
        
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.enable_thinking = enable_thinking
        self.auto_execute_tools = auto_execute_tools
        self.verbose = verbose
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        
        # Tool registry
        self.tools: Dict[str, Any] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
        
        # Conversation history
        self.messages: List[Dict[str, Any]] = []
        self.system_message: Optional[str] = None
        
    def set_system_message(self, message: str):
        """Set or update the system message."""
        self.system_message = message
        
    def register_tool(self, tool: Any):
        """
        Register a tool for the agent to use.
        
        Args:
            tool: Tool instance with execute() method and schema definition
        """
        tool_name = tool.name
        self.tools[tool_name] = tool
        
        # Build tool schema in OpenAI format
        schema = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool.description,
                "parameters": tool.get_parameters()
            }
        }
        self.tool_schemas.append(schema)
        
        if self.verbose:
            print(f"✓ Registered tool: {tool_name}")
        
    def unregister_tool(self, tool_name: str):
        """Remove a tool from the agent."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.tool_schemas = [
                s for s in self.tool_schemas 
                if s["function"]["name"] != tool_name
            ]
            
    def clear_tools(self):
        """Remove all registered tools."""
        self.tools.clear()
        self.tool_schemas.clear()
        
    def reset_conversation(self):
        """Clear conversation history."""
        self.messages.clear()
        
    def _prepare_messages(self, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Prepare messages including system message and optional context.
        
        Args:
            context: Optional contextual information to prepend to messages
            
        Returns:
            List of formatted messages
        """
        messages = []
        
        # Add system message
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        
        # Add context as system message if provided
        if context:
            messages.append({"role": "system", "content": f"CONTEXT:\n{context}"})
        
        # Add conversation history
        messages.extend(self.messages)
        
        return messages
        
    def _execute_tool_call(self, tool_call: Any) -> Dict[str, Any]:
        """
        Execute a single tool call.
        
        Args:
            tool_call: Tool call object from API response
            
        Returns:
            Tool execution result with metadata
        """
        call_id = tool_call.id
        function_name = tool_call.function.name
        arguments_str = tool_call.function.arguments
        
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "call_id": call_id,
                "function_name": function_name,
                "error": f"Failed to parse arguments: {e}",
                "content": json.dumps({"error": "Invalid JSON arguments"})
            }
            
        if function_name not in self.tools:
            return {
                "success": False,
                "call_id": call_id,
                "function_name": function_name,
                "error": f"Unknown function: {function_name}",
                "content": json.dumps({"error": f"Function '{function_name}' not found"})
            }
            
        try:
            tool = self.tools[function_name]
            if self.verbose:
                print(f"🔷 EXECUTING TOOL: {function_name} with args: {arguments}")
            
            result = tool.execute(**arguments)
            
            if self.verbose:
                print(f"🔷 TOOL RESULT: {result}")
            
            return {
                "success": True,
                "call_id": call_id,
                "function_name": function_name,
                "arguments": arguments,
                "result": result,
                "content": json.dumps(result)
            }
        except Exception as e:
            return {
                "success": False,
                "call_id": call_id,
                "function_name": function_name,
                "arguments": arguments,
                "error": str(e),
                "content": json.dumps({"error": str(e)})
            }
            
    def query(
        self,
        message: str,
        context: Optional[str] = None,
        max_tool_iterations: int = 5,
        return_metadata: bool = False
    ) -> str | Dict[str, Any]:
        """
        Send a query to the agent and get a response.
        
        Args:
            message: User message/query
            context: Optional contextual information (e.g., browser state, previous results)
            max_tool_iterations: Maximum number of tool calling rounds
            return_metadata: Return full metadata including tool calls
            
        Returns:
            Agent response as string, or dict with metadata if return_metadata=True
        """
        # Add user message
        self.messages.append({"role": "user", "content": message})
        
        tool_call_history = []
        iteration = 0
        
        while iteration < max_tool_iterations:
            iteration += 1
            
            # Prepare API call parameters
            call_params = {
                "model": self.model_name,
                "messages": self._prepare_messages(context),
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
            }
            
            # Add tools if available
            if self.tool_schemas:
                call_params["tools"] = self.tool_schemas
                
            # Add thinking mode configuration
            if not self.enable_thinking:
                call_params["extra_body"] = {
                    "chat_template_kwargs": {"enable_thinking": False}
                }
                
            # Call the API
            try:
                if self.verbose:
                    print(f"🔶 API CALL (iteration {iteration}) with {len(self.tool_schemas)} tools")
                
                response = self.client.chat.completions.create(**call_params)
                
                if self.verbose:
                    print(f"🔶 API RESPONSE - finish_reason: {response.choices[0].finish_reason}")
                
            except Exception as e:
                error_msg = f"API call failed: {e}"
                if self.verbose:
                    print(f"❌ {error_msg}")
                return error_msg
                
            choice = response.choices[0]
            message_obj = choice.message
            
            # WORKAROUND: LM Studio may return tool calls as text in content
            if not message_obj.tool_calls and message_obj.content:
                content_clean = message_obj.content.strip()
                content_clean = content_clean.replace("<end_of_turn>", "").strip()
                
                # Try to parse as JSON array of tool calls
                if content_clean.startswith("[") and "name" in content_clean and "arguments" in content_clean:
                    try:
                        tool_calls_json = json.loads(content_clean)
                        if isinstance(tool_calls_json, list):
                            if self.verbose:
                                print(f"🔶 WORKAROUND: Parsing {len(tool_calls_json)} tool calls from content")
                            
                            # Execute tool calls directly
                            for tc in tool_calls_json:
                                from types import SimpleNamespace
                                synthetic_call = SimpleNamespace(
                                    id=f"call_{tc.get('name')}_{len(tool_call_history)}",
                                    function=SimpleNamespace(
                                        name=tc.get("name"),
                                        arguments=json.dumps(tc.get("arguments", {}))
                                    )
                                )
                                result = self._execute_tool_call(synthetic_call)
                                tool_call_history.append(result)
                                
                                # Add result to messages
                                self.messages.append({
                                    "role": "tool",
                                    "content": result["content"],
                                    "tool_call_id": result["call_id"]
                                })
                            
                            # Add assistant message without tool_calls
                            self.messages.append({
                                "role": "assistant",
                                "content": None
                            })
                            
                            continue
                    except (json.JSONDecodeError, KeyError, AttributeError) as e:
                        if self.verbose:
                            print(f"🔶 Failed to parse content as tool calls: {e}")
            
            # Add assistant message to history
            self.messages.append(message_obj.model_dump())
            
            # Check if there are tool calls
            if not message_obj.tool_calls:
                # No tool calls, return the response
                content = message_obj.content or ""
                
                if return_metadata:
                    return {
                        "success": True,
                        "content": content,
                        "tool_calls": tool_call_history,
                        "iterations": iteration,
                        "finish_reason": choice.finish_reason
                    }
                return content
                
            # Execute tool calls if auto-execution is enabled
            if self.auto_execute_tools:
                for tool_call in message_obj.tool_calls:
                    result = self._execute_tool_call(tool_call)
                    tool_call_history.append(result)
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "tool",
                        "content": result["content"],
                        "tool_call_id": result["call_id"]
                    })
            else:
                # Return tool calls for manual execution
                calls_str = "\n".join([
                    f"- {tc.function.name}({tc.function.arguments})"
                    for tc in message_obj.tool_calls
                ])
                return f"Tool calls requested:\n{calls_str}"
                
        # Max iterations reached
        error_msg = f"Maximum tool iterations ({max_tool_iterations}) reached"
        if self.verbose:
            print(f"⚠️  {error_msg}")
        
        if return_metadata:
            return {
                "success": False,
                "error": error_msg,
                "content": self.messages[-1].get("content", "") if self.messages else "",
                "tool_calls": tool_call_history,
                "iterations": iteration
            }
        
        # Return the last message content if available
        if self.messages and self.messages[-1].get("content"):
            return self.messages[-1]["content"]
        
        return error_msg


if __name__ == "__main__":
    # Simple test
    print("OutlinesQwenAgent initialized successfully")
    agent = OutlinesQwenAgent(verbose=True)
    print(f"Agent ready with model: {agent.model_name}")
