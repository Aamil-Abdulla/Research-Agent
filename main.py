import os

from starlette.requests import Request
from langchain_azure_ai.agents.hosting import InvocationsHostServer

from graph import build_graph  # your existing, unchanged graph.py


def get_response_text(output: dict) -> str:
    return output.get("final_report", "")


class ResearchHostServer(InvocationsHostServer):
    async def parse_request(self, request: Request) -> tuple[str, bool]:
        data = await request.json()
        query = data.get("message", "")
        stream = bool(data.get("stream", False))
        return query, stream

    def build_input(self, parsed_data) -> dict:
        return {"query": parsed_data, "messages": []}


def main() -> None:
    graph = build_graph()
    port = int(os.environ.get("PORT", "8088"))
    ResearchHostServer(graph, output_parser=get_response_text).run(port=port)


if __name__ == "__main__":
    main()