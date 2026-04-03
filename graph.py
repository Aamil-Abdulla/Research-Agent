from sympy import content
from datetime import datetime
from langgraph.graph import StateGraph , END
from typing import TypedDict
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from tavily import TavilyClient

load_dotenv()


class ResearchState(TypedDict):
    query : str
    search_results : str
    summary : str
    final_report : str

tavily = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))
groq = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))


def search_nodes(state : ResearchState):
    print(f"Searching : {state['query']} ")
    results = tavily.search(query = state["query"], max_results = 5)

    content =""
    for r in results["results"]:
        content += f"Title: {r['title']}\nContent: {r['content']}\n\n"
    return {"search_results": content}

def summarize_nodes(state : ResearchState):
    print(f"Summarizing results ...")
    prompt = f"""
Summarize the following search results in a concise manner, highlighting the key points and insights:

    {state["search_results"]}
Summary:
"""
    response = groq.invoke(prompt)
    return {"summary" :response.content}

def report_nodes(state : ResearchState):
    print(f"Generating report ...")
    prompt = f"""
    Based on this summary, write a structured research report with:
    - Overview
    - Key Findings
    - Conclusion
    {state["summary"]}
Report: 
    """
    response = groq.invoke(prompt)
    report_text = response.content

    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/report_{timestamp}.md"
    with open(filename, "w",encoding="utf-8") as f:
        f.write(f"Research Report\n\n")
        f.write(f"**Query:** {state['query']}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Summary:**\n{state['summary']}\n\n")
        f.write(f"**Full Report:**\n{report_text}\n")
        f.write(f"---\n\n")
    print(f"Report saved :  {filename}")
    return {"final_report" : report_text}


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("search", search_nodes)
    graph.add_node("summarize", summarize_nodes)
    graph.add_node("report", report_nodes)

    graph.set_entry_point("search")
    graph.add_edge("search", "summarize")
    graph.add_edge("summarize", "report")
    graph.add_edge("report", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"query" : "latest AI tools 2026"})
    print("\nFinal Result:")
    print(result)

