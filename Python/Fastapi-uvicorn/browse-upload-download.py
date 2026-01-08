from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import shutil
import uvicorn

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 📂 Browse files
@app.get("/", response_class=HTMLResponse)
def browse():
    files = "".join(
        f'<li><a href="/download/{f.name}">{f.name}</a></li>'
        for f in UPLOAD_DIR.iterdir() if f.is_file()
    )

    return f"""
    <html>
        <body>
            <h2>File Browser</h2>

            <h3>Upload a file</h3>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <button type="submit">Upload</button>
            </form>

            <h3>Files</h3>
            <ul>
                {files or "<li>No files yet</li>"}
            </ul>
        </body>
    </html>
    """

# ⬆️ Upload
@app.post("/upload")
def upload(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

# ⬇️ Download
@app.get("/download/{filename}")
def download(filename: str):
    file_path = UPLOAD_DIR / filename
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
