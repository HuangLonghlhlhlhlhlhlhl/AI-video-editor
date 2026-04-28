import sqlite3
import json
import os

DB_PATH = "video_assets.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            tags TEXT,
            highlights TEXT,
            description TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def is_video_scanned(file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM videos WHERE file_path = ?', (file_path,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def insert_video_data(file_path, tags, highlights, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO videos (file_path, tags, highlights, description)
        VALUES (?, ?, ?, ?)
    ''', (file_path, json.dumps(tags), json.dumps(highlights), description))
    conn.commit()
    conn.close()

def get_all_videos():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos ORDER BY analyzed_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    videos = []
    for row in rows:
        vid = dict(row)
        vid['tags'] = json.loads(vid['tags']) if vid['tags'] else []
        vid['highlights'] = json.loads(vid['highlights']) if vid['highlights'] else []
        videos.append(vid)
    return videos
