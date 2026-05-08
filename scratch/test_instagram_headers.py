import yt_dlp

def test_instagram_reel_with_custom_headers():
    url = "https://www.instagram.com/reels/C6m_qR_S-6Y/"
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"Title: {info.get('title')}")
            print(f"Thumbnail: {info.get('thumbnail')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_instagram_reel_with_custom_headers()
