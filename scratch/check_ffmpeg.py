import shutil
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    ffmpeg_path = shutil.which("ffmpeg")
    print(f"FFmpeg Path: {ffmpeg_path}")
    
    import subprocess
    if ffmpeg_path:
        res = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True)
        print(f"FFmpeg version: {res.stdout.splitlines()[0]}")
    else:
        print("FFmpeg not found even with static_ffmpeg")
except ImportError:
    print("static_ffmpeg not installed")
except Exception as e:
    print(f"Error: {e}")
