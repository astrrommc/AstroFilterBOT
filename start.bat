@echo off
cd /d C:\Users\Astrr\AstroFilterBOT
call venv\Scripts\activate
git fetch
python autoupdate.py
pause