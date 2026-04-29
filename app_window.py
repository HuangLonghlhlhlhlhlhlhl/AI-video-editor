import webview
import threading
import uvicorn
import time
import requests
from main import app

class Api:
    def __init__(self):
        self.window = None

    def browse_directory(self):
        if self.window:
            result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
            if result and len(result) > 0:
                return result[0]
        return None

    def save_project_dialog(self):
        if self.window:
            result = self.window.create_file_dialog(webview.SAVE_DIALOG, file_types=('Gravity Project (*.gravity)', 'All files (*.*)'))
            return result
        return None

    def open_project_dialog(self):
        if self.window:
            result = self.window.create_file_dialog(webview.OPEN_DIALOG, file_types=('Gravity Project (*.gravity)', 'All files (*.*)'))
            if result and len(result) > 0:
                return result[0]
        return None

    def import_media_dialog(self):
        if self.window:
            result = self.window.create_file_dialog(webview.OPEN_DIALOG, multiselect=True, file_types=('Video files (*.mp4;*.mov;*.avi;*.mkv)', 'All files (*.*)'))
            return result
        return None

def run_server():
    # Run the FastAPI server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

if __name__ == '__main__':
    # Start the FastAPI server in a background thread
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    
    # Wait until the server is responsive
    server_ready = False
    for _ in range(30):
        try:
            requests.get("http://127.0.0.1:8000/")
            server_ready = True
            break
        except:
            time.sleep(0.1)
            
    if server_ready:
        api = Api()
        # Create a native OS window displaying the web app
        window = webview.create_window(
            "AI 编导助手 - 智能素材库", 
            "http://127.0.0.1:8000", 
            width=1280, 
            height=800,
            background_color='#0F172A',
            min_size=(1024, 768),
            js_api=api
        )
        api.window = window
        webview.start()
    else:
        print("Error: Could not start the local backend server.")
