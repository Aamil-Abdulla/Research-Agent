import os
import json
import logging
from datetime import datetime, timezone

from starlette.requests import Request
from langchain_azure_ai.agents.hosting import InvocationsHostServer

from graph import build_graph

logger = logging.getLogger(__name__)


def get_response_text(output: dict) -> str:
    """
    Returns the response field. Per InvocationsHostServer contract,
    this must be plain text — NOT a JSON blob. Sources/trace are logged
    separately so they land in Application Insights, not stuffed into
    the client-facing response.
    """
    report = output.get("final_report", "")
    sources = output.get("sources", [])
    execution_trace = output.get("execution_trace", {})

    logger.info(
        "agent_execution_complete",
        extra={
            "query": execution_trace.get("query", ""),
            "source_count": len(sources),
            "sources": sources,
            "execution_trace": execution_trace,
        },
    )

    return report


class ResearchHostServer(InvocationsHostServer):
    async def parse_request(self, request: Request) -> tuple[str, bool]:
        data = await request.json()
        query = data.get("message", "")
        stream = bool(data.get("stream", False))
        logger.info(f"Incoming request: query={query!r}, stream={stream}")
        return query, stream

    def build_input(self, parsed_data) -> dict:
        return {
            "query": parsed_data,
            "messages": [],
            "execution_trace": {},
        }


def main() -> None:
    graph = build_graph()
    port = int(os.environ.get("PORT", "8088"))
    logger.info(f"Starting Research Agent on port {port}")
    ResearchHostServer(graph, output_parser=get_response_text).run(port=port)


if __name__ == "__main__":
    main()