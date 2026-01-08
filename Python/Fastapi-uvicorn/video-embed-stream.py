from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pathlib import Path
import uvicorn

app = FastAPI()

VIDEO_PATH = Path("video.mp4")

def iter_file(path: Path, start: int, end: int, chunk_size=1024 * 1024):
    with path.open("rb") as f:
        f.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            chunk = f.read(min(chunk_size, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <body>
            <h2>Video Player</h2>
            <video width="640" controls>
                <source src="/video" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </body>
    </html>
    """

@app.get("/video")
def video(request: Request):
    if not VIDEO_PATH.exists():
        raise HTTPException(status_code=404)

    file_size = VIDEO_PATH.stat().st_size
    range_header = request.headers.get("range")

    if range_header:
        start, end = range_header.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else file_size - 1

        return StreamingResponse(
            iter_file(VIDEO_PATH, start, end),
            status_code=206,
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(end - start + 1),
            },
        )

    return StreamingResponse(
        iter_file(VIDEO_PATH, 0, file_size - 1),
        media_type="video/mp4",
        headers={"Content-Length": str(file_size)}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
