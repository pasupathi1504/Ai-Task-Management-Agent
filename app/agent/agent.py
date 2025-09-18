import os
import google.generativeai as genai
from typing import TypedDict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    AIMessage,
)
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition
import json

from .tools import create_task, update_task, delete_task, list_tasks, filter_tasks

# === Configure Gemini ===
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
llm = ChatGoogleGenerativeAI(model=MODEL_NAME)

TOOLS = [create_task, update_task, delete_task, list_tasks, filter_tasks]

class ToolExecutor:
    def __init__(self, tools):
        for tool in tools:
            print(f" - {tool} ({type(tool)})")
        self.tools = {}
        for tool in tools:
            if hasattr(tool, "name"):
                self.tools[tool.name] = tool
            elif isinstance(tool, dict) and "name" in tool:
                self.tools[tool["name"]] = tool
            else:
                raise ValueError(f"Tool {tool} has no 'name' attribute or key")

    def invoke(self, tool_calls):
        results = []
        for call in tool_calls:
            # Support both object and dict style tool calls
            if hasattr(call, "name") and hasattr(call, "args"):
                tool_name = call.name
                tool_args = call.args
            elif isinstance(call, dict):
                tool_name = call.get("name")
                tool_args = call.get("args", {})
            else:
                raise ValueError(f"Tool call {call} is not valid")
            tool = self.tools.get(tool_name)
            if tool:
                # Use .invoke() instead of calling as a function
                results.append(tool.invoke(tool_args))
            else:
                results.append(f"Tool {tool_name} not found")
        return results
    
tool_executor = ToolExecutor(TOOLS)
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = SystemMessage(
    content="""
You are a Task Manager AI. Use tools (create_task, update_task, delete_task, list_tasks, filter_tasks) to manage tasks.

- Always call a tool when the user asks to perform a task-related action.
- If a tool result includes {"success": false, "error": "..."} — explain the failure clearly to the user.
- Never ignore tool errors. Do not make up success messages.
- If tool call was successful, summarize it politely.
"""
)

class AgentState(TypedDict):
    messages: List[BaseMessage]

# === LLM node ===
def call_model(state: AgentState) -> AgentState:
    messages = [SYSTEM_PROMPT] + state["messages"]

    print(">>> DEBUG: Messages to LLM")
    for m in messages:
        print(f" - {m.__class__.__name__}: {getattr(m, 'content', '')}")

    response = llm_with_tools.invoke(messages)
    return {"messages": state["messages"] + [response]}

# === Tool executor node ===
def call_tools(state: AgentState) -> AgentState:
    messages = state["messages"]
    last_message = messages[-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return state  # Nothing to do

    tool_outputs = tool_executor.invoke(last_message.tool_calls)
    tool_messages = [
        ToolMessage(
            tool_call_id=tc.id if hasattr(tc, "id") else tc.get("id"),
            content=json.dumps(output) 
        )
        for tc, output in zip(last_message.tool_calls, tool_outputs)
    ]
    return {"messages": state["messages"] + tool_messages}

# === LangGraph wiring ===
graph = StateGraph(AgentState)
graph.add_node("llm", call_model)
graph.add_node("tools", call_tools)

graph.set_entry_point("llm")

# if tools were requested → run tools → then back to llm
graph.add_conditional_edges("llm", tools_condition, {
    "tools": "tools",
    END: END
})
graph.add_edge("tools", "llm")

workflow = graph.compile()
