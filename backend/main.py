from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from pathlib import Path

# ── App setup ──────────────────────────────────────────────
app = FastAPI(
    title="APEX Intelligence",
    description="India's AI Business Brain for SMEs",
    version="1.0.0"
)

# ── CORS — allows browser to call the API ──────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve frontend files ────────────────────────────────────
frontend_path = Path(__file__).parent.parent / "frontend"

if frontend_path.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(frontend_path)),
        name="static"
    )

# ── Routes ─────────────────────────────────────────────────

@app.get("/")
async def serve_dashboard():
    """Serve the main APEX dashboard"""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(
        {"message": "APEX is running. Put index.html in the frontend folder."},
        status_code=200
    )

@app.get("/api/health")
async def health_check():
    """Check if the server is running"""
    return {
        "status": "healthy",
        "app": "APEX Intelligence",
        "version": "1.0.0",
        "message": "Server is running successfully"
    }

@app.get("/api/demo-data")
async def get_demo_data():
    """Return demo business data for the dashboard"""
    return {
        "months":   ["J","F","M","A","M","J","J","A","S","O","N","D"],
        "revenue":  [42, 38.5, 51.2, 47.8, 63.4, 58.9,
                     71.2, 69.8, 78.5, 82.1, 79.4, 95.6],
        "expenses": [31, 29.5, 34.2, 32.8, 41.4, 39.9,
                     45.2, 44.8, 49.5, 52.1, 50.4, 58.6],
        "kpis": {
            "total_revenue": 777900,
            "net_profit":    235100,
            "profit_margin": 30.2,
            "customers":     2847,
            "churn_rate":    2.3,
            "yoy_growth":    34.7
        },
        "products": [
            {"name": "Product C", "revenue": 210000, "growth": 28.7},
            {"name": "Product E", "revenue": 189000, "growth": 18.9},
            {"name": "Product A", "revenue": 145000, "growth": 12.4},
            {"name": "Product B", "revenue": 98000,  "growth": -3.2},
            {"name": "Product D", "revenue": 67000,  "growth": 5.1},
        ],
        "segments": [
            {"name": "Enterprise",  "pct": 35},
            {"name": "Mid-Market",  "pct": 25},
            {"name": "SME",         "pct": 22},
            {"name": "Startup",     "pct": 12},
            {"name": "Individual",  "pct": 6},
        ],
        "geo": [
            {"region": "North America", "share": 40.1},
            {"region": "India",         "share": 32.5},
            {"region": "Europe",        "share": 15.1},
            {"region": "Asia Pacific",  "share": 8.5},
            {"region": "Other",         "share": 3.8},
        ]
    }

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Accept a CSV file upload from the user.
    Returns the parsed rows so the frontend can process them.
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files are accepted. Please export your data as CSV."
        )

    # Read file content
    try:
        content = await file.read()
        text    = content.decode("utf-8")
    except UnicodeDecodeError:
        # Try alternative encoding common in Indian Windows machines
        try:
            text = content.decode("latin-1")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Could not read file. Please save your file as UTF-8 CSV."
            )

    # Parse CSV
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        raise HTTPException(
            status_code=400,
            detail="File is empty or has no data rows."
        )

    headers = [h.strip().lower().replace('"','').replace("'","")
               for h in lines[0].split(",")]
    rows = []
    for line in lines[1:]:
        values = [v.strip().replace('"','').replace("'","")
                  for v in line.split(",")]
        row = {}
        for i, header in enumerate(headers):
            row[header] = values[i] if i < len(values) else ""
        rows.append(row)

    return {
        "success":  True,
        "filename": file.filename,
        "headers":  headers,
        "rows":     rows[:500],   # limit to 500 rows
        "total_rows": len(rows),
        "message":  f"Successfully loaded {len(rows)} rows from {file.filename}"
    }

@app.post("/api/save-user")
async def save_user(data: dict):
    """
    Save user account data.
    In production this would write to a database.
    For now it confirms receipt.
    """
    name  = data.get("name", "")
    biz   = data.get("biz", "")
    email = data.get("email", "")

    if not name or not email:
        raise HTTPException(status_code=400, detail="Name and email are required.")

    return {
        "success": True,
        "message": f"Account created for {name} at {biz}",
        "user": {"name": name, "biz": biz, "email": email}
    }

@app.get("/api/user-data/{email}")
async def get_user_data(email: str):
    """
    Get saved data for a specific user.
    In production this would query a database.
    Returns empty for now — data is stored in browser localStorage.
    """
    return {
        "success": True,
        "email":   email,
        "data":    None,
        "message": "Data is stored locally in the browser for this version."
    }

# ── Run server ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  🚀  APEX Intelligence Server Starting...")
    print("="*55)
    print("  📊  Dashboard  →  http://localhost:8000")
    print("  📖  API Docs   →  http://localhost:8000/docs")
    print("  ✅  Health     →  http://localhost:8000/api/health")
    print("="*55)
    print("  Press Ctrl+C to stop the server")
    print("="*55 + "\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )