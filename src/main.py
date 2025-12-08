import os
from typing import TypedDict, List   
from langgraph.graph import StateGraph, END
from tavily import TavilyClient
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

load_dotenv()
API_KEY = os.getenv("API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

tavily = TavilyClient(api_key=TAVILY_API_KEY)

llm = ChatGroq(
    api_key=API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)


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
    
    if ("NOTFULL" in draft_feedback):
        query = f"""generate short search query
        for {original_task}
        focusing on missing info: {draft_feedback}
        query: <short query (max 40 characters, min 10)>"""
        
        response = llm.invoke([HumanMessage(content=query)])
        original_task = response.content.strip()
        print(f"Generated short search query: {original_task}")
        
    search_response = tavily.search(query=original_task, max_results=5)
    results = [result['content'] for result in search_response['results']]
    
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
    User requests: {state['task']}
    Research results: {results}
    
    ONLY ANSWER WITH 'FULL' OR 'NOTFULL: reason'.
    If the answer is sketchy or incomplete, respond with:
    NOTFULL: <short reason (max 40 characters, min 10)>
    """
    
    response = llm.invoke([HumanMessage(content=critique_prompt)])
    decision = response.content.strip().upper()
    print(f"Critique decision: {decision}")
    
    # Lưu tạm ở draft
    return {
        "draft": decision
    }
    

def write_node(state: AgentState):
    print("Drafting the final output...")
    results = "\n".join(state["search_results"])
    draft_prompt = f"""
    You are an expert writer.
    User requests: {state['task']}
    Search results: {results}
    
    Based on the search results, write a short, 
    concise report on user topic.
    """
    
    response = llm.invoke([HumanMessage(content=draft_prompt)])
    draft = response.content.strip()
    
    return {
        "draft": draft
    }
    
    
def should_continue(state: AgentState):
    decision = state["draft"]
    count = state["count"]
    
    if count >= 3:
        print("Đã tìm quá 3 lần, bắt buộc viết bài.")
        return "write"
    
    if ("NOTFULL" in decision):
        print("Nội dung chưa đầy đủ, tiếp tục tìm kiếm.")
        return "search"
    
    return "write"


graph = StateGraph(AgentState)

graph.add_node("search", search_node)
graph.add_node("critique", critique_node)
graph.add_node("write", write_node)

graph.set_entry_point("search")

graph.add_edge("search", "critique")
graph.add_conditional_edges("critique", should_continue, {
    "search": "search",
    "write": "write"
})

graph.add_edge("write", END)

app = graph.compile()

topic = "Mô hình ngôn ngữ Gemini 1.5 Flash"

input_data = {
    "task": topic,
    "search_results": [], 
    "count": 0,           
    "draft": ""          
}

print(f"--- Bắt đầu Agent với chủ đề: {topic} ---")
try:
    result = app.invoke(input_data)
    print("\n\n=== KẾT QUẢ BÀI VIẾT ===")
    print(result["draft"])
except Exception as e:
    print(f"Có lỗi xảy ra: {e}")