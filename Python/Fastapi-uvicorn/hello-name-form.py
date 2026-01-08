from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# example http://127.0.0.1:8000/

@app.get("/", response_class=HTMLResponse)
def form():
    return """
    <html>
        <body>
            <h2>Enter your name</h2>
            <form action="/hello" method="post">
                <input type="text" name="name" required>
                <button type="submit">Submit</button>
            </form>
        </body>
    </html>
    """

@app.post("/hello", response_class=HTMLResponse)
def hello(name: str = Form(...)):
    return f"""
    <html>
        <body>
            <span style="color: green;">Hello</span>
            <span style="color: blue; font-weight: bold;">{name}</span>
            <br><br>
            <a href="/">Go back</a>
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
