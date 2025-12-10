import os
import random
import sqlite3
from typing import List, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from tavily import TavilyClient

load_dotenv()
API_KEY = os.getenv("API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

tavily = TavilyClient(api_key=TAVILY_API_KEY)

# ChatGroq model
"""llm = ChatGroq(
    api_key=API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)"""

# Ollama model
llm = ChatOllama(model="qwen2.5:7b-instruct")


class AgentState(TypedDict):
    task: str
    search_results: List[str]
    draft: str
    count: int


def search_node(state: AgentState):
    original_task = state["task"]
    draft_feedback = state.get("draft", "")
    count = state.get("count", 0)

    print(f"Performing search #{count + 1} for query: {original_task}")

    if "NOTFULL" in draft_feedback:
        query = f"""You are a helper optimized for generating search query.
        Task: Generate the best search query to find specific missing details.
        Original Topic: {original_task}
        Missing Details: {draft_feedback}
        Constraint: Output ONLY the query string. No quotes, no explanations, no preamble.
        """

        response = llm.invoke([HumanMessage(content=query)])
        original_task = str(response.content).strip()
        print(f"Generated short search query: {original_task}")

    search_response = tavily.search(query=original_task, max_results=5)
    results = [result["content"] for result in search_response["results"]]

    current_results = state.get("search_results", [])
    updated_results = current_results + results
    return {
        "search_results": updated_results,
        "count": count + 1,
    }


def critique_node(state: AgentState):
    print("Critiquing research results...")
    results = "\n".join(state["search_results"])
    critique_prompt = f"""
    You are a tough critic,
    User requests: {state["task"]}
    Research results: {results}
    
    ONLY ANSWER WITH 'FULL' OR 'NOTFULL: reason'.
    If the answer is sketchy or incomplete, respond with:
    NOTFULL: <reason why it's not full>
    FULL: <no reason>.
    """

    response = llm.invoke([HumanMessage(content=critique_prompt)])
    decision = str(response.content).strip().upper()
    print(f"Critique decision: {decision}")

    # Lưu tạm ở draft
    return {"draft": decision}


def write_node(state: AgentState):
    print("Drafting the final output...")
    results = "\n".join(state["search_results"])
    draft_prompt = f"""
    You are an expert writer.
    User requests: {state["task"]}
    Search results: {results}
    
    Based on the search results, write a short, 
    concise report on user topic.
    """

    response = llm.invoke([HumanMessage(content=draft_prompt)])
    draft = str(response.content).strip()

    BASE = os.path.dirname(os.path.abspath(__file__))
    OUTPUT = os.path.join(BASE, "..", "output_txt")

    os.makedirs(OUTPUT, exist_ok=True)

    # Tạo 4 chữ số ngẫu nhiên
    rand_id = str(random.randint(1000, 9999))

    file_path = os.path.join(OUTPUT, f"final_draft_{rand_id}.md")

    with open(file_path, "w", encoding="utf-8") as f:
        print(f"Saving final draft to {file_path}")
        f.write(draft)

    return {"draft": draft}


def should_continue(state: AgentState):
    decision = state["draft"]
    count = state["count"]

    if count >= 3:
        print("Đã tìm quá 3 lần, bắt buộc viết bài.")
        return "write"

    if "NOTFULL" in decision:
        print("Nội dung chưa đầy đủ, tiếp tục tìm kiếm.")
        return "search"

    return "write"


graph = StateGraph(AgentState)

graph.add_node("search", search_node)
graph.add_node("critique", critique_node)
graph.add_node("write", write_node)

graph.set_entry_point("search")

graph.add_edge("search", "critique")
graph.add_conditional_edges(
    "critique", should_continue, {"search": "search", "write": "write"}
)

graph.add_edge("write", END)

conn = sqlite3.connect("memory.db", check_same_thread=False)
memory = SqliteSaver(conn)
app = graph.compile(checkpointer=memory)

if __name__ == "__main__":
    topic = "What is the impact of AI on the job market?"
    input = {"task": topic}
    result = app.invoke(input)  # type: ignore
    print(result["draft"])
