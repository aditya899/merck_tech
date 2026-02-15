from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_first_upload_creates_single_upload():
    csv_content = (
        "Drug Name,Target,Efficacy,Quantity\n"
        "Aspirin,COX-1,0.85,10\n"
        "Ibuprofen,COX-2,0.78,10\n"
    ).encode("utf-8")

    files = {"file": ("sample.csv", csv_content, "text/csv")}
    resp = client.post("/api/upload", files=files)

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    rows = resp.json()
    assert len(rows) == 2

    # API data should expose one upload with filename and rows
    resp_data = client.get("/api/data")
    assert resp_data.status_code == 200
    uploads = resp_data.json()
    assert len(uploads) == 1
    upload = uploads[0]

    assert upload["filename"] == "sample.csv"
    assert len(upload["rows"]) == 2
    assert set(upload["columns"]) == {"Drug Name", "Target", "Efficacy", "Quantity"}


def test_multiple_uploads_are_preserved_with_filenames():
    # first upload
    csv1 = (
        "col1,col2\n"
        "a,1\n"
    ).encode("utf-8")
    files1 = {"file": ("first.csv", csv1, "text/csv")}
    resp1 = client.post("/api/upload", files=files1)
    assert resp1.status_code == 200

    # second upload
    csv2 = (
        "x,y,z\n"
        "p,2,foo\n"
        "q,3,bar\n"
    ).encode("utf-8")
    files2 = {"file": ("second.csv", csv2, "text/csv")}
    resp2 = client.post("/api/upload", files=files2)
    assert resp2.status_code == 200

    # now /api/data should have two uploads, in order
    resp_data = client.get("/api/data")
    assert resp_data.status_code == 200
    uploads = resp_data.json()
    assert len(uploads) == 3 or len(uploads) >= 2  # depends if previous tests ran; check last two

    # verify the last two uploads specifically (most recent behavior)
    first = uploads[-2]
    second = uploads[-1]

    assert first["filename"] == "first.csv"
    assert first["rows"][0]["col1"] == "a"
    assert first["rows"][0]["col2"] == "1"

    assert second["filename"] == "second.csv"
    assert len(second["rows"]) == 2
    assert second["rows"][0]["x"] == "p"
    assert second["rows"][0]["y"] == "2"
    assert second["rows"][0]["z"] == "foo"


def test_upload_rejects_non_csv():
    csv_content = "a,b,c\n1,2,3\n".encode("utf-8")
    files = {"file": ("bad.txt", csv_content, "text/plain")}

    resp = client.post("/api/upload", files=files)

    assert resp.status_code == 400
    body = resp.json()
    assert "Only CSV files are allowed" in body["detail"]
