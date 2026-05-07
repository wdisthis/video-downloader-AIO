from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import re
import time
import shutil
from urllib.parse import unquote
import threading

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    FFMPEG_PATH = shutil.which("ffmpeg")
except Exception:
    FFMPEG_PATH = None

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

app.config['DOWNLOAD_FOLDER'] = 'downloads'

if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
    os.makedirs(app.config['DOWNLOAD_FOLDER'])

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.youtube.com/"
}

def clean_filename(filename):
    cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
    return cleaned[:100].strip()

def get_youtube_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'http_headers': HEADERS
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            avail_res = sorted(list(set(f.get('height') for f in formats if f.get('height') and f.get('vcodec') != 'none')), reverse=True)
            
            tech_formats = []
            for f in formats:
                if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                    tech_formats.append({
                        'ext': f.get('ext'),
                        'res': f"{f.get('height')}p" if f.get('height') else 'Audio',
                        'note': f.get('format_note', ''),
                        'vcodec': f.get('vcodec'),
                        'acodec': f.get('acodec'),
                        'filesize': f.get('filesize')
                    })

            return {
                'success': True,
                'title': info.get('title', 'Tidak Diketahui'),
                'duration': info.get('duration_string', 'N/A'),
                'thumbnail': info.get('thumbnail', ''),
                'author': info.get('uploader', 'Tidak Diketahui'),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', '')[:100],
                'available_resolutions': [f"{r}p" for r in avail_res],
                'formats_table': tech_formats[:15]
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info_route():
    data = request.get_json()
    url = data.get('url')
    if not url: return jsonify({'success': False, 'error': 'No URL provided'})
    return jsonify(get_youtube_info(url))

@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.get_json()
    url = data.get('url')
    dtype = data.get('type', 'audio')
    
    timestamp = int(time.time())
    file_id = f"{dtype}_{timestamp}"
    
    if dtype == 'video':
        res = data.get('resolution', '720p').replace('p', '')
        # Force H.264 (avc1) and AAC (mp4a) for compatibility
        f_str = f'bestvideo[height<={res}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<={res}][ext=mp4]/best'
        ext = 'mp4' # Always use mp4 for video as requested
    else:
        ext = data.get('format', 'mp3')
        f_str = 'bestaudio/best'

    ydl_opts = {
        'format': f_str,
        'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], f'{file_id}.%(ext)s'),
        'quiet': True,
        'http_headers': HEADERS,
        'ffmpeg_location': FFMPEG_PATH,
    }
    
    if dtype == 'video':
        ydl_opts['merge_output_format'] = 'mp4'
    
    if dtype == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': ext,
            'preferredquality': data.get('quality', '192'),
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = clean_filename(info.get('title', 'file'))
            final_name = f"{title}.{ext}"
            
            for f in os.listdir(app.config['DOWNLOAD_FOLDER']):
                if f.startswith(file_id):
                    src = os.path.join(app.config['DOWNLOAD_FOLDER'], f)
                    dst = os.path.join(app.config['DOWNLOAD_FOLDER'], final_name)
                    if os.path.exists(dst): os.remove(dst)
                    os.rename(src, dst)
                    return jsonify({'success': True, 'filename': final_name, 'download_url': f"/api/file/{final_name}"})
            return jsonify({'success': False, 'error': 'File not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/files')
def list_files():
    files = []
    for f in os.listdir(app.config['DOWNLOAD_FOLDER']):
        path = os.path.join(app.config['DOWNLOAD_FOLDER'], f)
        if os.path.isfile(path):
            files.append({
                'name': f,
                'size': f"{os.path.getsize(path) / (1024*1024):.2f} MB",
                'time': time.ctime(os.path.getmtime(path))
            })
    return jsonify(files)

@app.route('/api/file/<filename>')
def serve_file(filename):
    path = os.path.join(app.config['DOWNLOAD_FOLDER'], unquote(filename))
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)