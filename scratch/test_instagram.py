import yt_dlp

def test_instagram_reel():
    url = "https://www.instagram.com/reels/C6m_qR_S-6Y/" # Example reel URL (random one)
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"Title: {info.get('title')}")
            print(f"Thumbnail: {info.get('thumbnail')}")
            print(f"Formats: {len(info.get('formats', []))}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_instagram_reel()
