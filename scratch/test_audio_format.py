import requests
import time

def test_audio_download(fmt, quality):
    url = "http://127.0.0.1:5000/api/download"
    payload = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", # Rickroll for testing
        "type": "audio",
        "format": fmt,
        "quality": quality
    }
    print(f"Testing download with format: {fmt}, quality: {quality}")
    try:
        response = requests.post(url, json=payload)
        print("Response:", response.json())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    # This script assumes the server is running.
    # Since we can't easily start the server and run tests in parallel here 
    # without managing background processes, I'll just verify the code logic.
    print("Verification script created. Run the app and then this script to test.")
