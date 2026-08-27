from datetime import datetime,timezone
from langgraph.graph import StateGraph , END
from typing import Annotated, TypedDict
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from langgraph.graph.message import add_messages
import logging
load_dotenv()

class SourceMetadata(TypedDict):
    """Structured source for enterprise auditability"""
    title: str
    url: str
    source: str
    retrieved_at: str

class ResearchState(TypedDict):
    query : str
    search_results : str
    summary : str
    final_report : str
    messages: Annotated[list, add_messages]
    execution_trace:dict
    sources: list[SourceMetadata]



tavily = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))
groq = ChatGroq(model="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_nodes(state : ResearchState):
    """
    Retrieve sources with full metadata capture.
    Enterprise: Every retrieval is logged for audit trail.
    """
    start_time = datetime.now(timezone.utc).isoformat()
    print(f"[SEARCH] Query: {state['query']} | Time: {start_time}")
    try:
        results = tavily.search(query = state["query"], max_results = 5)
    except Exception as e:
        logger.error(f"Tavily retrieval failed: {e}")
        raise
    content =""
    sources=[]
    for r in results["results"]:
        content += f"Title: {r['title']}\nContent: {r['content']}\n\n"

        source = {
            "title": r["title"],
            "url": r.get("url",""),
            "source": r.get("source",""),
            "retrieved_at": start_time

        }
        sources.append(source)

    logger.info(f"Retrieval Complete: {len(sources)} sources for query: {state['query']}")
    return {
        "search_results": content,
        "sources": sources,
        "execution_trace": {
            "search_timestamp":start_time,
            "source_count": len(sources)
        }

    }

def summarize_nodes(state : ResearchState):
    """
    Summarize with source context.
    Enterprise: Summarization is traceable to sources.
    """
    start_time = datetime.now(timezone.utc).isoformat()
    print(f"[SUMMARIZE] Processing {len(state['sources'])} sources | Time: {start_time}")
    source_context = "\n".join([f"Title: {s['title']}, URL: {s['url']}, Source: {s['source']}, Retrieved At: {s['retrieved_at']}" for s in state["sources"]])
    prompt = f"""
Summarize the following search results in a concise manner, highlighting the key points and insights:
    Source Context for Attribution:
    {source_context}
    Content to Summarize:
    {state["search_results"]}
    Provide a Focused Summary :
"""
    try:
        response = groq.invoke(prompt)
    except Exception as e:
        logger.error(f"Groq summarization failed: {e}")
        raise
    logger.info(f"Summarization Complete | Input Sources: {len(state['sources'])}")
    return {
        "summary" :response.content,
        "sources": state.get("sources", []),
        "execution_trace": {
            **state.get("execution_trace", {}),
            "summarize_timestamp": start_time

        }}

def report_nodes(state: ResearchState):
    """
    Generate structured report with full source attribution.
    Enterprise: Final output includes source lineage for compliance/audit.
    """
    print("Generating report...")
    start_time = datetime.now(timezone.utc).isoformat()
    print(f"[REPORT] Generating report| Time: {start_time}")
    source_listed = "\n".join([
        f"[{i+1}] {s['title']}: {s['url']}"
        for i, s in enumerate(state["sources"])
    ])
    prompt = f"""
    Based on this summary, write a structured research report with:
    - Overview
    - Key Findings
    - Conclusion
    - Sources( cite the following if relevant):
    Sources Available:
    {source_listed}
    Summary:
    {state["summary"]}
    Generate a professional research Report: 
    """
    try:
        response = groq.invoke(prompt)
    except Exception as e:
        logger.error(f"Groq report generation failed: {e}")
        raise

    execution_trace = {
        **state.get("execution_trace", {}),
        "report_timestamp": start_time,
        "total_sources": len(state["sources"]),
        "query": state["query"]
    }
    logger.info(f"Report Generation Complete | Total Execution Trace: {execution_trace}")
    return {
        "final_report": response.content,
        "sources": state.get("sources", []),
        "execution_trace": execution_trace
    }


def build_graph():
    """Build Enterprise-grade Langgraph Pipeline"""
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
    result = app.invoke({
        "query": "latest AI tools 2026",
        "messages": [],
        "execution_trace": {},
    })
    print("\n" + "="*60)
    print("FINAL REPORT:")
    print("="*60)
    print(result["final_report"])
    print("\n" + "="*60)
    print("SOURCES USED (FOR AUDIT TRAIL):")
    print("="*60)
    for i, src in enumerate(result.get("sources", []), 1):
        print(f"[{i}] {src['title']}")
        print(f"    URL: {src['url']}")
        print(f"    Retrieved: {src['retrieved_at']}")
    print("\n" + "="*60)
    print("EXECUTION TRACE (FOR FOUNDRY MONITORING):")
    print("="*60)
    import json
    print(json.dumps(result.get("execution_trace", {}), indent=2))