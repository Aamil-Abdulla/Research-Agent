# 🔍 LangGraph Research Agent

An autonomous AI research agent that searches the web, summarizes findings, and generates structured research reports — all in one click.

🌐 **Live Demo:** [research-agent-cwvv.onrender.com](https://research-agent-cwvv.onrender.com/)

---
---
## What It Does

1. User enters a research query
2. Agent searches the web in real time using **Tavily API**
3. **Groq (Llama 3.1)** summarizes the results
4. A structured report is generated with Overview, Key Findings, and Conclusion
5. User can download the report as a `.md` file instantly

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | LangGraph |
| LLM | Groq — Llama 3.1 8B Instant |
| Web Search | Tavily API |
| Backend | FastAPI |
| Frontend | HTML, CSS, Vanilla JS |
| Containerization | Docker |
| Deployment | Render |

---

## How It Works

```
User Query
    ↓
[search_node]     — Tavily searches web, returns top 5 results
    ↓
[summarize_node]  — Groq summarizes the results
    ↓
[report_node]     — Groq writes structured report (Overview, Key Findings, Conclusion)
    ↓
Frontend displays Summary + Full Report + Download button
```

Each node reads and writes to a shared `ResearchState` TypedDict — LangGraph manages state propagation automatically.

---

## Run Locally

### Prerequisites
- Python 3.10+
- Tavily API key — [get one free](https://tavily.com)
- Groq API key — [get one free](https://console.groq.com)

### Setup

```bash
git clone https://github.com/Aamil-Abdulla/Research-Agent.git
cd Research-Agent
pip install -r requirements.txt
```

Create a `.env` file:

```
TAVILY_API_KEY=your_tavily_key
GROQ_API_KEY=your_groq_key
```

Run the app:

```bash
uvicorn main:app --reload
```

Open `http://localhost:8000`

### Run with Docker

```bash
docker build -t research-agent .
docker run -p 8000:8000 --env-file .env research-agent
```

---

## Project Structure

```
Research-Agent/
├── graph.py        # LangGraph pipeline (3 nodes)
├── main.py         # FastAPI (2 endpoints)
├── index.html      # Frontend UI
├── Dockerfile      # Container config
├── requirements.txt
└── .env            # API keys (never commit)
```

---

## Author

**Aamil Abdulla** — [LinkedIn](https://linkedin.com/in/aamil-abdulla-868996248) · [GitHub](https://github.com/Aamil-Abdulla)
