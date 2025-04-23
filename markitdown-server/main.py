import asyncio
from playwright.async_api import async_playwright
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from markitdown import MarkItDown
import io
from openai import OpenAI
import os
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# 静的ファイルとしてHTMLをマウント
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    contents = await file.read()
    md = MarkItDown()
    result = md.convert(io.BytesIO(contents))
    return JSONResponse(content={"filename": file.filename, "markdown": result.text_content})


@app.post("/convert/html")
async def convert_html(html: str = Body(..., media_type="text/plain")):
    """
    HTML文字列をMarkdownに変換します。
    """
    md = MarkItDown()
    html_bytes = html.encode("utf-8")
    result = md.convert(io.BytesIO(html_bytes))
    return JSONResponse(content={"markdown": result.text_content})


@app.post("/convert/url")
async def convert_url(request: dict = Body(...)):
    try:
        url = request.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()
            await browser.close()

        md = MarkItDown()
        result = md.convert(io.BytesIO(content.encode('utf-8')))
        return JSONResponse(content={"markdown": result.text_content})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert/img")
async def convert_img(file: UploadFile = File(...)):
    """
    画像ファイルをMarkdownに変換します。
    """
    contents = await file.read()
    client = OpenAI(
        base_url=f"{OLLAMA_HOST}/v1",
        api_key='ollama',
    )
    md = MarkItDown()
    md = MarkItDown(llm_client=client, llm_model="PetrosStav/gemma3-tools:12b")
    result = md.convert(io.BytesIO(contents))
    return JSONResponse(content={"filename": file.filename, "markdown": result.text_content})
