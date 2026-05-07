import yt_dlp
import os
import shutil
import static_ffmpeg

static_ffmpeg.add_paths()
FFMPEG_PATH = shutil.which("ffmpeg")
print(f"FFMPEG_PATH: {FFMPEG_PATH}")

url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ" # Short video
res = "720"
f_str = f'bestvideo[height<={res}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<={res}][ext=mp4]/best'

ydl_opts = {
    'format': f_str,
    'outtmpl': 'test_download.%(ext)s',
    'ffmpeg_location': FFMPEG_PATH,
    'merge_output_format': 'mp4',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("Check if test_download.mp4 exists and has reasonable size.")
if os.path.exists("test_download.mp4"):
    print(f"File exists: {os.path.getsize('test_download.mp4')} bytes")
else:
    print("File not found.")
