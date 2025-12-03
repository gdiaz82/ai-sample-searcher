from fastapi import FastAPI
from pydantic import BaseModel
from searcher import SampleSearcher

app = FastAPI()

searcher = SampleSearcher(db_path="./demo_db") 

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
def search(req: SearchRequest):
    results = searcher.search(req.query, top_k=3)
    return {"results": results}