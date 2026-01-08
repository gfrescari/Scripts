from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# example: http://127.0.0.1:8000/hello?name=John
app = FastAPI()

@app.get("/hello", response_class=HTMLResponse)
def hello(name: str):
    return f"""
    <html>
        <body>
            <span style="color: green;">Hello</span>
            <span style="color: blue; font-weight: bold;">{name}</span>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
