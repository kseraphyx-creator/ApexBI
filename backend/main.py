from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from pathlib import Path

app = FastAPI(title="APEX Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def serve():
    return FileResponse(str(frontend_path / "index.html"))

@app.get("/api/health")
async def health():
    return {"status": "healthy", "app": "APEX Intelligence"}

@app.get("/api/data")
async def get_data():
    return {
        "revenue":  [42,38.5,51.2,47.8,63.4,58.9,71.2,69.8,78.5,82.1,79.4,95.6],
        "expenses": [31,29.5,34.2,32.8,41.4,39.9,45.2,44.8,49.5,52.1,50.4,58.6],
        "months":   ["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"],
        "kpis": {
            "total_revenue": 777900,
            "net_profit":    235100,
            "customers":     2847,
            "churn_rate":    2.3,
            "mom_growth":    8.4,
            "yoy_growth":    34.7
        },
        "products": [
            {"name":"Product C","rev":"$210k","growth":"+28.7%","pos":True,"bar":100},
            {"name":"Product E","rev":"$189k","growth":"+18.9%","pos":True,"bar":90},
            {"name":"Product A","rev":"$145k","growth":"+12.4%","pos":True,"bar":69},
            {"name":"Product B","rev":"$98k", "growth":"-3.2%", "pos":False,"bar":47},
            {"name":"Product D","rev":"$67k", "growth":"+5.1%", "pos":True,"bar":32}
        ],
        "segments": [
            {"name":"Enterprise","pct":35,"color":"#00e5b0"},
            {"name":"Mid-Market","pct":25,"color":"#7c6aff"},
            {"name":"SME",       "pct":22,"color":"#ff6b35"},
            {"name":"Startup",   "pct":12,"color":"#00b4ff"},
            {"name":"Individual","pct":6, "color":"#ff4560"}
        ],
        "geo": [
            {"flag":"🇺🇸","name":"North America","share":40.1},
            {"flag":"🇮🇳","name":"India",        "share":32.5},
            {"flag":"🇪🇺","name":"Europe",       "share":15.1},
            {"flag":"🌏","name":"Asia Pacific",  "share":8.5},
            {"flag":"🌎","name":"Other",         "share":3.8}
        ]
    }

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files supported")
    content = await file.read()
    lines   = content.decode("utf-8").strip().split("\n")
    headers = [h.strip() for h in lines[0].split(",")]
    rows    = []
    for line in lines[1:]:
        vals = line.split(",")
        row  = {headers[i]: vals[i].strip()
                for i in range(min(len(headers), len(vals)))}
        rows.append(row)
    return {"headers": headers, "rows": rows[:100], "total": len(rows)}

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  APEX Intelligence is running!")
    print("  Open this in Chrome:")
    print("  http://localhost:8000")
    print("="*50 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)