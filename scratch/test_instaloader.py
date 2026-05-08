import instaloader

def test_instaloader_reel():
    L = instaloader.Instaloader()
    url = "https://www.instagram.com/reels/C6m_qR_S-6Y/"
    # Extract shortcode from URL
    # URL format: https://www.instagram.com/reels/SHORTCODE/
    import re
    match = re.search(r'reels/([^/?#&]+)', url)
    if not match:
        print("Invalid URL")
        return
    shortcode = match.group(1)
    print(f"Shortcode: {shortcode}")

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"Title/Caption: {post.caption[:50]}...")
        print(f"Video URL: {post.video_url}")
        print(f"Is Video: {post.is_video}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_instaloader_reel()
