import os
import sys
import time
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

import database

# Load environment variables
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Use the latest Flash model for multimodal tasks
MODEL_NAME = "gemini-1.5-flash" 

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

def default_logger(level, msg):
    print(f"[{level.upper()}] {msg}")

def get_video_files(directory):
    video_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in VIDEO_EXTENSIONS:
                video_files.append(os.path.join(root, file))
    return video_files

def analyze_video_with_gemini(file_path, logger=default_logger):
    filename = os.path.basename(file_path)
    logger("info", f"Uploading {filename} to Gemini...")
    try:
        video_file = genai.upload_file(path=file_path)
    except Exception as e:
        logger("error", f"Failed to upload video {filename}: {e}")
        return None

    logger("info", f"Uploaded as {video_file.name}. Waiting for processing...")
    
    # Wait for the file to finish processing
    while video_file.state.name == "PROCESSING":
        time.sleep(5)
        video_file = genai.get_file(video_file.name)
        
    if video_file.state.name == "FAILED":
        logger("error", f"Video processing failed for {video_file.name}")
        genai.delete_file(video_file.name)
        return None

    logger("info", f"Processing complete. Analyzing semantics for {filename}...")
    
    prompt = """
    Please analyze this video for a video editing assistant tool.
    Output the result as a valid JSON object with the following schema:
    {
        "description": "A brief overall summary of what happens in the video.",
        "tags": ["tag1", "tag2", "tag3"], // Semantic tags (e.g., emotion, lighting, action, scene type, object)
        "highlights": [
            {
                "timestamp_start": "00:00",
                "timestamp_end": "00:05",
                "description": "What happens in this highlight, why it's good for editing",
                "vibe": "energetic/peaceful/etc"
            }
        ]
    }
    Make sure your response is only the JSON object, without markdown formatting if possible.
    """
    
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
    )
    
    model = genai.GenerativeModel(model_name=MODEL_NAME)
    
    try:
        response = model.generate_content(
            [video_file, prompt],
            generation_config=generation_config
        )
        
        result_text = response.text
        if result_text.startswith("```json"):
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif result_text.startswith("```"):
            result_text = result_text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(result_text)
        
        # Clean up the file from Gemini storage
        genai.delete_file(video_file.name)
        
        return data
    except Exception as e:
        logger("error", f"Error analyzing video {filename}: {e}")
        try:
            genai.delete_file(video_file.name)
        except:
            pass
        return None

def scan_files(file_paths, logger=default_logger):
    if not os.getenv("GEMINI_API_KEY"):
        logger("error", "GEMINI_API_KEY is not configured in .env file.")
        return

    logger("info", "Initializing database...")
    database.init_db()

    logger("info", f"Processing {len(file_paths)} specific file(s)...")

    for video_path in file_paths:
        abs_path = os.path.abspath(video_path)
        filename = os.path.basename(video_path)
        
        if database.is_video_scanned(abs_path):
            logger("info", f"Skipping already scanned video: {filename}")
            continue
            
        logger("info", f"--- Processing: {filename} ---")
        analysis_data = analyze_video_with_gemini(abs_path, logger=logger)
        
        if analysis_data:
            description = analysis_data.get("description", "")
            tags = analysis_data.get("tags", [])
            highlights = analysis_data.get("highlights", [])
            
            database.insert_video_data(abs_path, tags, highlights, description)
            logger("success", f"Successfully analyzed and stored metadata for {filename}")
        else:
            logger("error", f"Failed to extract metadata for {filename}")

    logger("done", "Import completed!")

def scan_directory(target_dir, logger=default_logger):
    if not os.path.isdir(target_dir):
        logger("error", f"Directory '{target_dir}' does not exist.")
        return

    if not os.getenv("GEMINI_API_KEY"):
        logger("error", "GEMINI_API_KEY is not configured in .env file.")
        return

    logger("info", "Initializing database...")
    database.init_db()

    logger("info", f"Scanning directory '{target_dir}' for videos...")
    videos = get_video_files(target_dir)
    logger("info", f"Found {len(videos)} video(s).")

    scan_files(videos, logger=logger)

def main():
    parser = argparse.ArgumentParser(description="AI Video Assets Scanner")
    parser.add_argument("directory", help="Directory containing videos to scan")
    args = parser.parse_args()
    scan_directory(args.directory)

if __name__ == "__main__":
    main()
