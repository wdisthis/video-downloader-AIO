from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import re
import time
import shutil
from urllib.parse import unquote
import threading
import instaloader

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

def transcode_for_whatsapp(input_path, output_path):
    if not FFMPEG_PATH:
        return False
    
    # Strictly enforce H.264 and AAC without limiting FPS or resolution
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.1",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]
    
    try:
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"FFmpeg Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Transcode Exception: {e}")
        return False

def get_media_info(url, cookie_browser=None):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'http_headers': HEADERS
    }
    
    if cookie_browser and cookie_browser != 'none':
        ydl_opts['cookiesfrombrowser'] = (cookie_browser,)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Filter for WhatsApp compatible resolutions
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
                'formats_table': tech_formats[:15],
                'platform': info.get('extractor_key', 'Generic').lower()
            }
    except Exception as e:
        # Fallback for Instagram if yt-dlp fails
        if 'instagram' in url.lower():
            try:
                L = instaloader.Instaloader()
                shortcode_match = re.search(r'(?:reels|p|reel)/([^/?#&]+)', url)
                if shortcode_match:
                    shortcode = shortcode_match.group(1)
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    return {
                        'success': True,
                        'title': post.caption[:50] if post.caption else 'Instagram Reel',
                        'duration': 'N/A',
                        'thumbnail': post.url,
                        'author': post.owner_username,
                        'view_count': post.video_view_count if post.is_video else 0,
                        'description': post.caption[:100] if post.caption else '',
                        'available_resolutions': ['720p'],
                        'formats_table': [{'ext': 'mp4', 'res': '720p', 'note': 'High Quality', 'vcodec': 'h264', 'acodec': 'aac'}],
                        'platform': 'instagram'
                    }
            except Exception as ie:
                return {'success': False, 'error': f"Instagram Error: {str(ie)}"}
        
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info_route():
    data = request.get_json()
    url = data.get('url')
    browser = data.get('browser') # Optional browser for cookies
    if not url: return jsonify({'success': False, 'error': 'No URL provided'})
    return jsonify(get_media_info(url, browser))

@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.get_json()
    url = data.get('url')
    dtype = data.get('type', 'audio')
    browser = data.get('browser')
    
    timestamp = int(time.time())
    file_id = f"{dtype}_{timestamp}"
    
    if dtype == 'video':
        res = data.get('resolution', '720p').replace('p', '')
        # STRONGLY Force H.264 (avc1) and AAC (mp4a) for WhatsApp compatibility
        # We try to find pre-merged mp4 first, then specific h264+aac streams, then fallback to best and recode
        f_str = f'bestvideo[height<={res}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<={res}][ext=mp4]/best'
        ext = 'mp4'
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
    
    if browser and browser != 'none':
        ydl_opts['cookiesfrombrowser'] = (browser,)
    
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
            
            # Find the raw downloaded file
            raw_file = None
            for f in os.listdir(app.config['DOWNLOAD_FOLDER']):
                if f.startswith(file_id):
                    raw_file = os.path.join(app.config['DOWNLOAD_FOLDER'], f)
                    break
            
            if not raw_file:
                return jsonify({'success': False, 'error': 'Download failed - file not found'})

            final_name = f"{title}.{ext}"
            final_path = os.path.join(app.config['DOWNLOAD_FOLDER'], final_name)

            if dtype == 'video':
                # TRANSCODE FOR WHATSAPP
                temp_output = os.path.join(app.config['DOWNLOAD_FOLDER'], f"transcoded_{file_id}.mp4")
                success = transcode_for_whatsapp(raw_file, temp_output)
                
                if success:
                    if os.path.exists(final_path): os.remove(final_path)
                    os.rename(temp_output, final_path)
                    if os.path.exists(raw_file): os.remove(raw_file)
                else:
                    # Fallback to original if transcoding fails
                    if os.path.exists(final_path): os.remove(final_path)
                    os.rename(raw_file, final_path)
            else:
                # For audio, just rename
                if os.path.exists(final_path): os.remove(final_path)
                os.rename(raw_file, final_path)

            return jsonify({'success': True, 'filename': final_name, 'download_url': f"/api/file/{final_name}"})
            
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