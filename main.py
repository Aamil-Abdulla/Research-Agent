from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from graph import build_graph
from pydantic import BaseModel

app = FastAPI()
research_app = build_graph()

class Query_Request(BaseModel):
    query : str

@app.get("/")
async def home():
    with open("index.html" , "r") as f:
        return HTMLResponse(content = f.read())
    
@app.post("/research")
async def research(request : Query_Request):
    result = research_app.invoke({"query" : request.query})
    return {
        "query" : result["query"],
        "summary" : result["summary"],
        "final_report" : result["final_report"]
    }