import os
import subprocess
import tempfile
import threading
from datetime import datetime

export_state = {
    "is_exporting": False,
    "progress": 0,
    "status_text": "Idle",
    "output_file": "",
    "error": None
}

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def run_export_task(timeline, output_dir):
    if not check_ffmpeg():
        export_state["is_exporting"] = False
        export_state["error"] = "系统中未检测到 FFmpeg，请在终端执行 'brew install ffmpeg' 后重试。"
        return

    export_state["is_exporting"] = True
    export_state["progress"] = 0
    export_state["error"] = None
    export_state["output_file"] = ""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"AI_Export_{timestamp}.mp4")
    
    try:
        temp_dir = tempfile.mkdtemp()
        temp_clips = []
        total_clips = len(timeline)
        
        for idx, clip in enumerate(timeline):
            export_state["status_text"] = f"正在剪切片段 {idx+1}/{total_clips}..."
            export_state["progress"] = int((idx / total_clips) * 80)
            
            file_path = clip.get("file_path")
            start_time = clip.get("start_time", "00:00")
            end_time = clip.get("end_time", "00:05")
            
            temp_output = os.path.join(temp_dir, f"clip_{idx}.mp4")
            
            # Cut and normalize: 1080p, 30fps, standard h264/aac
            # padding handles different aspect ratios smoothly
            cmd = [
                "ffmpeg", "-y", 
                "-i", file_path,
                "-ss", str(start_time),
                "-to", str(end_time),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                "-r", "30",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-ar", "44100",
                temp_output
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            temp_clips.append(temp_output)
            
        export_state["status_text"] = "正在合成最终成片..."
        export_state["progress"] = 85
        
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, "w") as f:
            for clip_path in temp_clips:
                f.write(f"file '{clip_path}'\n")
                
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            output_path
        ]
        subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        export_state["progress"] = 100
        export_state["status_text"] = "渲染完成！"
        export_state["output_file"] = output_path
        
    except Exception as e:
        export_state["error"] = f"渲染失败: {str(e)}"
    finally:
        export_state["is_exporting"] = False

def start_export(timeline, output_dir):
    if export_state["is_exporting"]:
        return False
        
    t = threading.Thread(target=run_export_task, args=(timeline, output_dir))
    t.daemon = True
    t.start()
    return True
