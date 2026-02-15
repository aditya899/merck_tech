# Drug Discovery Analytics – FastAPI CSV Viewer

A small FastAPI web app to upload CSV files, store them in memory, and view all uploaded files (with their own headers and rows) via a basic HTML UI and REST APIs.

---

## 1. Features

- Upload a CSV file via a simple HTML form or REST API (`/upload`, `/api/upload`).
- Parse the CSV with whatever columns are present in the header row.
- Store each upload separately with:
  - `filename`
  - `columns` (all distinct header names)
  - `rows` (list of row dictionaries).
- View all previous uploads in the UI, grouped by file name, each with its own table.
- Retrieve all uploads as JSON via `/api/data`.
- Basic tests using `pytest` and `fastapi.testclient`.

---

## 2. Project structure

```text
merck_tech/
  app/
    __init__.py
    main.py          # FastAPI app, routes, CSV parsing
    db.py            # in-memory “database” of uploads
  templates/
    base.html        # shared layout
    index.html       # upload form + list of uploaded CSVs
    upload_result.html  # preview of last uploaded CSV
  tests/
    test_csv_upload.py
  sample.csv
  requirements.txt
  README.md
  ```

3. Setup and run (any machine)

    3.1. Prerequisites Python 3.10+ installed.

Git (if you clone from a repo).

3.2. Clone and create virtual environment
```
git clone <your-repo-url> merck_tech
cd merck_tech

python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```
Install Requirements
```pip install -r requirements.txt```

3.4. Run the app
```uvicorn app.main:app --reload```

Open in browser:

UI: http://127.0.0.1:8000/

API docs (Swagger UI): http://127.0.0.1:8000/docs


4. API description 

4.1. POST /api/upload 

Upload a CSV file and store it as a new “upload” entry.

# Request
````
Method: POST

Content‑Type: multipart/form-data

Field: file – CSV file with a header row.

Responses

200 OK – body is a JSON array of row objects ({ column_name: value }).

400 Bad Request – invalid content type or missing header row.

Example

curl -X POST "http://127.0.0.1:8000/api/upload" \
  -F "file=@sample.csv;type=text/csv"
Response

json
[
  {"Drug Name": "Aspirin", "Target": "COX-1", "Efficacy": "0.85", "Quantity": "10"},
  {"Drug Name": "Ibuprofen", "Target": "COX-2", "Efficacy": "0.78", "Quantity": "10"}
]
4.2. GET /api/data
Return all uploads with their filenames, column headers, and rows.

Request

Method: GET

Response

200 OK

Example

json
[
  {
    "filename": "sample.csv",
    "columns": ["Drug Name", "Target", "Efficacy", "Quantity"],
    "rows": [
      {"Drug Name": "Aspirin", "Target": "COX-1", "Efficacy": "0.85", "Quantity": "10"},
      {"Drug Name": "Ibuprofen", "Target": "COX-2", "Efficacy": "0.78", "Quantity": "10"}
    ]
  },
  {
    "filename": "another.csv",
    "columns": ["col1", "col2"],
    "rows": [
      {"col1": "a", "col2": "1"}
    ]
  }
]
4.3. GET /
HTML UI with upload form and list of all uploaded CSVs.

Shows a file picker and Upload button.

For each upload, displays:

heading: file name

table: headers from that file, rows from that file.

4.4. POST /upload
HTML form endpoint backing the UI.

Accepts a CSV file from the form, stores it, and renders upload_result.html with:

filename

number of imported records

table preview of that file’s rows.
````