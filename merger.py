import os
import sys
import shutil
import subprocess

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    FFMPEG_PATH = shutil.which("ffmpeg")
except Exception:
    FFMPEG_PATH = shutil.which("ffmpeg")

def merge_video_audio(video_path, audio_path, output_path):
    if not FFMPEG_PATH:
        print("Error: FFmpeg not found. Please install it or static-ffmpeg.")
        return False
    
    print(f"Merging:\n  Video: {video_path}\n  Audio: {audio_path}\n  Output: {output_path}")
    
    cmd = [
        FFMPEG_PATH,
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',       # Try to copy video stream (should be H.264 already)
        '-c:a', 'aac',        # Re-encode audio to AAC for safety
        '-strict', 'experimental',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        '-y',                 # Overwrite output
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Merge successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Merge failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python merger.py <video_file> <audio_file> <output_file>")
        sys.exit(1)
    
    v = sys.argv[1]
    a = sys.argv[2]
    o = sys.argv[3]
    
    if not os.path.exists(v):
        print(f"File not found: {v}")
        sys.exit(1)
    if not os.path.exists(a):
        print(f"File not found: {a}")
        sys.exit(1)
        
    merge_video_audio(v, a, o)
