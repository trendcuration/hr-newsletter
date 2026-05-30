@echo off
echo HR Weekly Brief 환경 설정
echo ========================

pip install -r requirements.txt

echo.
echo 환경변수 설정 방법:
echo   set ANTHROPIC_API_KEY=your_key_here
echo   set GMAIL_APP_PASSWORD=your_app_password_here
echo.
echo 미리보기 실행: python main.py --preview
echo 메일 발송 실행: python main.py
echo.
pause
