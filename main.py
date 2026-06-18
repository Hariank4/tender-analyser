from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import json
from docx_generator import generate_top_docx, generate_report_docx
from ai import analyse_tender, fix_eligibility_gaps

app = FastAPI(title="MeraPath Tender Analyser")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def home():
    return FileResponse("frontend/index.html")


@app.post("/analyse")
async def analyse(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return {"error": "Please upload a PDF file only"}
    
    pdf_bytes = await file.read()
    
    if len(pdf_bytes) < 1000:
        return {"error": "This PDF appears to be empty or corrupted"}
    
    try:
        data = analyse_tender(pdf_bytes)
        return data
    except Exception as e:
        error_msg = str(e)
        if "credit balance" in error_msg.lower():
            return {"error": "api_credits", "message": "Anthropic API credits needed. Add credits at console.anthropic.com → Billing"}
        elif "invalid_request" in error_msg.lower():
            return {"error": "invalid_pdf", "message": "Could not read this PDF. Make sure it contains selectable text, not a scanned image."}
        else:
            return {"error": "general", "message": f"Analysis failed: {error_msg}"}


@app.post("/download/top")
async def download_top(data: dict):
    docx_bytes = generate_top_docx(data)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=TOP.docx"}
    )


@app.post("/download/report")
async def download_report(data: dict):
    docx_bytes = generate_report_docx(data)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=Report.docx"}
    )
@app.post("/gaps")
async def get_gaps(data: dict):
    try:
        result = fix_eligibility_gaps(data)
        return result
    except Exception as e:
        error_msg = str(e)
        if "credit balance" in error_msg.lower():
            return {"error": "api_credits", "message": "API credits needed"}
        return {"error": "general", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)