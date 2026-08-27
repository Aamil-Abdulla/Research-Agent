"""
Runs the 6 designed evaluation queries against the live Foundry-hosted
research-agent (v4) and writes the results as a single-turn JSONL dataset
matching Foundry's Evaluation -> Existing dataset schema:
  {"query": ..., "response": ..., "context": ..., "ground_truth": ...}

ground_truth is intentionally left as an empty string for every row --
there's no pre-existing "correct answer" to grade against for open-ended
research queries, so groundedness/relevance evaluators should be scored
off `context` (the real retrieved sources) instead of `ground_truth`.
"""

import json
import time
import requests
from azure.identity import DefaultAzureCredential

# ---- CONFIG ----
PROJECT_ENDPOINT = "https://aamilabdulla0-1117-resource.services.ai.azure.com/api/projects/aamilabdulla0-1117"
INVOCATIONS_URL = f"{PROJECT_ENDPOINT}/agents/research-agent/endpoint/protocols/invocations"

OUTPUT_PATH = "eval_dataset.jsonl"

credential = DefaultAzureCredential()

QUERIES = [
    "Compare LangGraph and Microsoft Agent Framework for building AI agents",
    "What is Agent365 and what can it do?",
    "What are current AI governance and audit standards for enterprise AI agents?",
    "What is BCG X and what AI capabilities does it offer?",
    "What are current best practices for LLM observability?",
    "What is OX Alpha and what makes it notable?",
]


def invoke_agent(query: str) -> dict:
    # Fresh token per call -- cheap, and avoids expiry issues on a run that
    # takes several minutes across 6 queries.
    token = credential.get_token("https://ai.azure.com/.default").token

    resp = requests.post(
        INVOCATIONS_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        params={"api-version": "v1"},
        json={"message": query},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    rows = []
    for i, query in enumerate(QUERIES, start=1):
        print(f"[{i}/{len(QUERIES)}] Invoking agent: {query!r}")
        try:
            result = invoke_agent(query)
        except Exception as e:
            print(f"  FAILED: {e}")
            continue

        # main.py's InvocationsHostServer returns {'response': '<plain markdown>'}
        # per the v4 fix -- sources/execution_trace go to App Insights via
        # logging, not the client response. So we don't have structured
        # "context" from this call alone.
        response_text = result.get("response", "")

        row = {
            "query": query,
            "response": response_text,
            # Context intentionally blank here -- see NOTE below on how to
            # fill this from App Insights if you want source-grounded context
            # rather than an empty field.
            "context": "",
            "ground_truth": "",
        }
        rows.append(row)
        print(f"  OK ({len(response_text)} chars)")
        time.sleep(1)  # small buffer between calls

    with open(OUTPUT_PATH, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    print(f"\nWrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

# ------------------------------------------------------------------
# NOTE on `context`:
# Because v4's fix moved sources/execution_trace out of the client
# response and into the agent_execution_complete log line (App Insights),
# this script's context field will be empty by default -- it only has
# what /invocations actually returns, which is plain response text.
#
# To fill `context` with the real retrieved sources (recommended, since
# Groundedness evaluators score the response against context):
#   1. After running this script, go to App Insights -> Logs
#   2. Run: traces | where message contains "agent_execution_complete"
#   3. For each of the 6 queries, find its matching row (match on the query
#      text inside customDimensions) and pull the `sources` list
#   4. Paste each query's sources (e.g. "title: url" per source, newline
#      joined) into that row's "context" field in eval_dataset.jsonl
#
# This keeps the dataset honest: response is the agent's real output,
# context is the agent's real retrieved sources -- both from the live v4
# deployment, nothing hand-typed or guessed.
# ------------------------------------------------------------------