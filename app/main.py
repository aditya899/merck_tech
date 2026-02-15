# app/main.py
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict
from io import StringIO
import csv

from . import db

app = FastAPI(title="Drug Discovery Analytics Service")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """UI: upload form + list of all uploaded CSVs."""
    uploads = db.get_uploads()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "uploads": uploads,  # list of {filename, columns, rows}
        },
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_csv(request: Request, file: UploadFile = File(...)):
    if file.content_type not in ("text/csv", "application/vnd.ms-excel"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    contents = await file.read()
    text = contents.decode("utf-8")

    rows = _parse_csv(text)
    db.add_upload(file.filename, rows)

    # show preview for this upload only
    columns = sorted({c for r in rows for c in r.keys()})
    return templates.TemplateResponse(
        "upload_result.html",
        {
            "request": request,
            "filename": file.filename,
            "count": len(rows),
            "records": rows,
            "columns": columns,
        },
    )


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    if file.content_type not in ("text/csv", "application/vnd.ms-excel"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    contents = await file.read()
    text = contents.decode("utf-8")

    rows = _parse_csv(text)
    db.add_upload(file.filename, rows)
    return rows


@app.get("/api/data")
async def api_data():
    """Return all uploads, including filenames, columns, and rows."""
    return db.get_uploads()


def _parse_csv(csv_text: str) -> List[Dict]:
    buffer = StringIO(csv_text)
    reader = csv.DictReader(buffer)

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file has no header row")

    records: List[Dict] = []
    for row in reader:
        records.append(dict(row))
    return records
