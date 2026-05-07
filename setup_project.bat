@echo off
if not exist venv (
  python -m venv venv
)
call venv\Scripts\activate
pip install flask flask-cors yt-dlp
pip freeze > requirements.txt
if not exist static mkdir static
if not exist templates mkdir templates
if not exist downloads mkdir downloads
echo Setup selesai
