import subprocess
import os

def transcode_for_whatsapp(input_path, output_path, ffmpeg_path):
    # Standard WhatsApp-ready command
    cmd = [
        ffmpeg_path,
        "-y", # Overwrite
        "-i", input_path,
        "-c:v", "libx264",
        "-profile:v", "baseline",
        "-level", "3.0",
        "-pix_fmt", "yuv420p",
        "-vf", "scale='if(gt(iw,ih),min(1280,iw),-2)':'if(gt(iw,ih),-2,min(1280,ih))'", # Scale to 720p max (1280 long edge)
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-crf", "28", # High compression for WA
        output_path
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("Success")
    else:
        print(f"Error: {result.stderr}")

if __name__ == "__main__":
    # Test with a dummy file if needed, or just prepare the function for app.py
    pass
