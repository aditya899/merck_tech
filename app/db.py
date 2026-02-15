# app/db.py
from typing import List, Dict, Any
from threading import Lock

_lock = Lock()

# each item: {"filename": str, "columns": List[str], "rows": List[Dict[str, Any]]}
_uploads: List[Dict[str, Any]] = []


def clear_all() -> None:
    """Clear all uploads (if you want a reset endpoint)."""
    global _uploads
    with _lock:
        _uploads = []


def add_upload(filename: str, rows: List[Dict]) -> None:
    """Append a new upload with its own filename and columns."""
    global _uploads
    if not rows:
        return
    columns = sorted({c for row in rows for c in row.keys()})
    upload = {"filename": filename, "columns": columns, "rows": rows}
    with _lock:
        _uploads.append(upload)


def get_uploads() -> List[Dict[str, Any]]:
    """Return all uploads (oldest first)."""
    with _lock:
        return list(_uploads)
