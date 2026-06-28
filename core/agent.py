"""ReAct Agent — Autonomous reasoning and action loop.

The agent follows the ReAct pattern:
1. Think about the task
2. Choose an action (tool call)
3. Observe the result
4. Repeat until task is complete or max iterations reached
"""
import json
import os
from rich.console import Console
from rich.markdown import Markdown

from core.config import Config
from core.permissions import request_permission
from core.logger import log
from llm import ollama_provider
from tools.registry import get_all_tools, get_ollama_tools_schema, get_tool_by_name

console = Console()

AGENT_SYSTEM_PROMPT = """\
You are Chatty Nemotron, an autonomous coding agent operating in ReAct mode.
Working directory: {cwd}

You have these tools: read_file, write_file, search_replace, list_directory, glob_search, grep, execute_command.

IMPORTANT:
- Use relative paths (e.g. "." or "chatty_chronos") or the working directory shown above.
- For glob_search, use path="." and pattern="**/*.py" to find files recursively.
- For list_directory, use path="." to list the current directory.

For each step:
1. Think about what you need to do next
2. Use a tool to take action
3. Observe the result and decide next steps
4. When done, provide a final summary to the user

Be methodical. Break complex tasks into steps. Verify your work.
"""


class ReActAgent:
    def __init__(self, config: Config, max_iterations: int = 30, depth: int = 0):
        self.config = config
        self.max_iterations = max_iterations
        self.depth = depth
        self.model = config.get("model")
        self.provider = config.get("provider", "ollama")
        
        # Check if provider is a cloud provider
        from llm.fallback import get_available_providers
        self.cloud_provider = None
        for p in get_available_providers():
            if p["name"] == self.provider:
                self.cloud_provider = p
                break

        if self.provider == "llamacpp":
            self.host = config.get("llamacpp_host", "http://localhost:8080")
        else:
            self.host = config.get("ollama_host", "http://localhost:11434")
        self.tools_schema = get_ollama_tools_schema()
        cwd = os.getcwd()
        self.messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT.format(cwd=cwd)}]
        self.iteration = 0

    def run(self, task: str) -> str:
        """Execute a task autonomously. Returns final response."""
        self.messages.append({"role": "user", "content": task})
        self.iteration = 0

        console.print(f"\n  [bold cyan]Agent starting task[/bold cyan] (max {self.max_iterations} steps)")
        console.print(f"  [dim]{task[:80]}{'...' if len(task) > 80 else ''}[/dim]\n")

        while self.iteration < self.max_iterations:
            self.iteration += 1

            try:
                with console.status(f"[bold cyan]Agent thinking... (step {self.iteration}/{self.max_iterations})[/bold cyan]"):
                    if self.provider == "llamacpp":
                        from llm import llamacpp_provider
                        response = llamacpp_provider.chat(
                            self.messages, self.host, self.model, tools=self.tools_schema
                        )
                    elif self.cloud_provider:
                        from llm import openai_provider
                        # Determine active model (if user overrode model in config, use it, otherwise use provider's default)
                        active_model = self.config.get("model") or self.cloud_provider.get("model")
                        response = openai_provider.chat(
                            self.messages,
                            base_url=self.cloud_provider["base_url"],
                            api_key_name=self.cloud_provider["env_key"],
                            model=active_model,
                            tools=self.tools_schema
                        )
                    else:
                        response = ollama_provider.chat(
                            self.messages, self.model, self.host, tools=self.tools_schema
                        )
            except Exception as e:
                log.error(f"Agent LLM error (step {self.iteration}): {e}", exc_info=True)
                console.print(f"  [red]Agent error: {e}[/red]")
                return f"Agent failed: {e}"

            # Tool calls — execute and continue
            if response.message.tool_calls:
                # Add assistant message to history
                self.messages.append({
                    "role": "assistant",
                    "content": response.message.content or "",
                    "tool_calls": [
                        {"function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in response.message.tool_calls
                    ]
                })

                # Show thinking if present
                if response.message.content:
                    console.print(f"  [dim]Step {self.iteration}:[/dim] {response.message.content[:100]}")

                # Execute tools
                for tc in response.message.tool_calls:
                    result = self._execute_tool(tc)
                    self.messages.append({"role": "tool", "content": result})

                continue

            # No tool calls — final response
            final = response.message.content or ""
            self.messages.append({"role": "assistant", "content": final})

            console.print(f"\n  [bold green]Agent completed in {self.iteration} step(s)[/bold green]\n")
            console.print(Markdown(final))
            console.print()
            return final

        # Hit max iterations
        console.print(f"\n  [yellow]Agent reached {self.max_iterations} iterations. Stopping.[/yellow]\n")
        return "Agent reached maximum iterations without completing the task."

    def run_stream(self, task: str):
        """Execute a task autonomously, yielding events for UI consumption."""
        self.messages.append({"role": "user", "content": task})
        self.iteration = 0

        while self.iteration < self.max_iterations:
            self.iteration += 1
            yield {"type": "status", "content": f"Agent se gândește... (pasul {self.iteration}/{self.max_iterations})"}

            try:
                if self.provider == "llamacpp":
                    from llm import llamacpp_provider
                    response = llamacpp_provider.chat(
                        self.messages, self.host, self.model, tools=self.tools_schema
                    )
                elif self.cloud_provider:
                    from llm import openai_provider
                    active_model = self.config.get("model") or self.cloud_provider.get("model")
                    response = openai_provider.chat(
                        self.messages,
                        base_url=self.cloud_provider["base_url"],
                        api_key_name=self.cloud_provider["env_key"],
                        model=active_model,
                        tools=self.tools_schema
                    )
                else:
                    response = ollama_provider.chat(
                        self.messages, self.model, self.host, tools=self.tools_schema
                    )
            except Exception as e:
                log.error(f"Agent LLM error (step {self.iteration}): {e}", exc_info=True)
                yield {"type": "error", "content": f"Eroare LLM agent: {e}"}
                return

            # Tool calls — execute and continue
            if response.message.tool_calls:
                tool_calls_payload = [
                    {"function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in response.message.tool_calls
                ]
                self.messages.append({
                    "role": "assistant",
                    "content": response.message.content or "",
                    "tool_calls": tool_calls_payload
                })

                yield {"type": "tool_calls", "content": tool_calls_payload}

                # Execute each tool call
                for tc in response.message.tool_calls:
                    yield {"type": "status", "content": f"Executare instrument: {tc.function.name}..."}
                    result = self._execute_tool(tc)
                    self.messages.append({"role": "tool", "content": result})
                    yield {"type": "tool_result", "name": tc.function.name, "result": result}

                continue

            # No tool calls — final response
            final = response.message.content or ""
            self.messages.append({"role": "assistant", "content": final})
            yield {"type": "token", "content": final}
            break
        else:
            yield {"type": "error", "content": "Agentul a atins numărul maxim de pași."}

    def _execute_tool(self, tool_call) -> str:
        """Execute a tool call with permission checks."""
        func_name = tool_call.function.name
        args = tool_call.function.arguments

        tool = get_tool_by_name(func_name)
        if not tool:
            return f"Error: Unknown tool '{func_name}'"

        # Permission check for dangerous tools
        if tool.requires_permission:
            desc = f"{func_name}({', '.join(f'{k}={repr(v)[:40]}' for k, v in args.items())})"
            if not request_permission(func_name, desc):
                return "Permission denied by user."

        # Show what's happening
        args_preview = ", ".join(f"{k}={repr(v)[:30]}" for k, v in args.items())
        console.print(f"  [dim]  [{self.iteration}] {func_name}({args_preview})[/dim]")

        # Pass config and agent depth if the tool signature accepts them
        extra_args = {}
        import inspect
        sig = inspect.signature(tool.execute)
        if "config" in sig.parameters:
            extra_args["config"] = self.config
        if "depth" in sig.parameters:
            extra_args["depth"] = self.depth

        result = tool.execute(**args, **extra_args)

        # Show brief result
        result_preview = result[:80].replace("\n", " ")
        console.print(f"  [dim]      -> {result_preview}{'...' if len(result) > 80 else ''}[/dim]")

        return result
