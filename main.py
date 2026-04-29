from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import threading
import os
import json
from collections import defaultdict
import google.generativeai as genai

from scanner import scan_directory
import database
import export_engine

# Configure Gemini for Smart Edit
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

app = FastAPI()

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state for simple logging
scan_state = {
    "is_scanning": False,
    "logs": []
}

class ScanRequest(BaseModel):
    directory: str

def scan_worker(directory: str):
    scan_state["is_scanning"] = True
    scan_state["logs"] = []
    
    def logger(level, msg):
        scan_state["logs"].append({"level": level, "message": msg})
        
    try:
        scan_directory(directory, logger=logger)
    except Exception as e:
        logger("error", f"Scanner error: {e}")
    finally:
        scan_state["is_scanning"] = False

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/api/videos")
async def get_videos():
    videos = database.get_all_videos()
    return {"videos": videos}

@app.get("/api/media")
async def get_media(path: str):
    if os.path.exists(path):
        return FileResponse(path)
    return {"status": "error", "message": "File not found"}

@app.get("/api/videos/grouped")
async def get_grouped_videos():
    videos = database.get_all_videos()
    tag_counts = defaultdict(int)
    for v in videos:
        for tag in v.get('tags', []):
            tag_counts[tag] += 1
            
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    top_tags = [t[0] for t in sorted_tags[:10]]
    
    groups = defaultdict(list)
    ungrouped = []
    
    for v in videos:
        assigned = False
        for tag in v.get('tags', []):
            if tag in top_tags:
                groups[tag].append(v)
                assigned = True
                break
        if not assigned:
            ungrouped.append(v)
            
    if ungrouped:
        groups["未归类"] = ungrouped
        
    return {"groups": groups}

class EditRequest(BaseModel):
    prompt: str

@app.post("/api/edit")
async def generate_edit_plan(req: EditRequest):
    videos = database.get_all_videos()
    if not videos:
        return {"status": "error", "message": "素材库为空，请先扫描素材"}
        
    metadata_list = []
    for v in videos:
        metadata_list.append({
            "id": v["id"],
            "file_path": v["file_path"],
            "description": v["description"],
            "tags": v["tags"],
            "highlights": v["highlights"]
        })
        
    prompt_str = f"""
    You are an expert AI video editor. The user wants to create a video based on this request: "{req.prompt}"
    
    Here is the available raw footage metadata:
    {json.dumps(metadata_list, ensure_ascii=False)}
    
    Please create an edit plan by selecting the best clips from the available highlights.
    Output a JSON object with this schema:
    {{
        "title": "Suggested Title for the Video",
        "rationale": "Why you chose these clips",
        "timeline": [
            {{
                "video_id": 123,
                "file_path": "/path/to/video.mp4",
                "start_time": "00:00",
                "end_time": "00:05",
                "description": "What this clip adds to the story",
                "transition": "cut / crossfade"
            }}
        ]
    }}
    Ensure output is ONLY the JSON object. Do not include markdown formatting like ```json.
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        generation_config = genai.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt_str, generation_config=generation_config)
        
        result_text = response.text
        if result_text.startswith("```json"):
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif result_text.startswith("```"):
            result_text = result_text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(result_text)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

from scanner import scan_directory, scan_files

class FileImportRequest(BaseModel):
    files: list

def import_worker(files: list):
    scan_state["is_scanning"] = True
    scan_state["logs"] = []
    
    def logger(level, msg):
        scan_state["logs"].append({"level": level, "message": msg})
        
    try:
        scan_files(files, logger=logger)
    except Exception as e:
        logger("error", f"Import error: {e}")
    finally:
        scan_state["is_scanning"] = False

@app.post("/api/import/files")
async def start_import_files(req: FileImportRequest, background_tasks: BackgroundTasks):
    if scan_state["is_scanning"]:
        return {"status": "error", "message": "A scan or import is already in progress"}
    
    background_tasks.add_task(import_worker, req.files)
    return {"status": "success", "message": "Import started"}

@app.post("/api/scan")
async def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    if scan_state["is_scanning"]:
        return {"status": "error", "message": "A scan or import is already in progress"}
    
    background_tasks.add_task(scan_worker, req.directory)
    return {"status": "success", "message": "Scan started"}

@app.get("/api/status")
async def get_status():
    return {
        "is_scanning": scan_state["is_scanning"],
        "logs": scan_state["logs"]
    }

class ExportRequest(BaseModel):
    timeline: list
    output_dir: str

@app.post("/api/export")
async def start_export(req: ExportRequest):
    success = export_engine.start_export(req.timeline, req.output_dir)
    if not success:
        return {"status": "error", "message": "导出任务已在进行中"}
    return {"status": "success", "message": "导出已开始"}

@app.get("/api/export/status")
async def get_export_status():
    return export_engine.export_state

if __name__ == "__main__":
    import uvicorn
    print("Starting AI Video Editor Assistant on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
