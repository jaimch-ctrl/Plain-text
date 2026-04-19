from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/warrant/top")
def get_top(stock: str):
    return {
        "stock": stock,
        "top": {
            "code": "033872",
            "name": f"{stock} 模擬權證",
            "volume": 2060
        },
        "top3": [
            {"code": "033872", "volume": 2060},
            {"code": "044111", "volume": 1500},
            {"code": "055222", "volume": 1200}
        ]
    }
