from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from pathlib import Path

app = FastAPI(
    title="APEX Intelligence",
    description="India's AI Business Brain for SMEs",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = Path(__file__).parent.parent / "frontend"

if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def serve_dashboard():
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"error": "index.html not found in frontend folder"})

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "app": "APEX Intelligence v3.0",
        "message": "Server running successfully"
    }

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files accepted. Please export as CSV."
        )
    try:
        content = await file.read()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")

        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]

        if len(lines) < 2:
            raise HTTPException(
                status_code=400,
                detail="File has no data rows"
            )

        headers = [
            h.strip().lower().replace('"', '').replace("'", "")
            for h in lines[0].split(",")
        ]

        rows = []
        for line in lines[1:]:
            values = [
                v.strip().replace('"', '').replace("'", "")
                for v in line.split(",")
            ]
            row = {
                headers[i]: values[i] if i < len(values) else ""
                for i in range(len(headers))
            }
            rows.append(row)

        return {
            "success": True,
            "filename": file.filename,
            "headers": headers,
            "rows": rows[:500],
            "total_rows": len(rows),
            "message": f"Successfully loaded {len(rows)} rows"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("\n" + "="*52)
    print("  🚀  APEX Intelligence v3.0 is running!")
    print("="*52)
    print("  📊  Dashboard  →  http://localhost:8000")
    print("  📖  API Docs   →  http://localhost:8000/docs")
    print("  ✅  Health     →  http://localhost:8000/api/health")
    print("="*52)
    print("  Press Ctrl+C to stop")
    print("="*52 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)