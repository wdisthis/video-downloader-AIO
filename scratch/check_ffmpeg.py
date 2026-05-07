import static_ffmpeg
import os

try:
    static_ffmpeg.add_paths()
    print("FFmpeg paths added.")
    # Check if ffmpeg is now in path or find where it is
    import shutil
    ffmpeg_path = shutil.which("ffmpeg")
    print(f"FFmpeg path: {ffmpeg_path}")
except Exception as e:
    print(f"Error: {e}")
