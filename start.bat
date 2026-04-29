@echo off
chcp 65001 >nul
title ChatBook - 실행 중...

echo ======================================
echo   ChatBook 실행 (Portable 환경^)
echo ======================================
echo.

:: 프로젝트 루트로 이동
cd /d "%~dp0"

:: 포터블 Node 환경 변수 추가 (pnpm 인식용)
set "PATH=%~dp0runtime\node;%PATH%"

:: 백엔드 실행 (새 창^)
echo [1/2] 백엔드 서버 시작 (port 8000^)...
cd /d "%~dp0backend"
set "PYTHONPATH=%cd%"
start "ChatBook Backend" cmd /k "..\runtime\python\python.exe -m uvicorn app.main:app --port 8000 --host 127.0.0.1"
cd /d "%~dp0"

:: 잠시 대기
timeout /t 3 /nobreak >nul

:: pnpm 설치 확인
where pnpm >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] pnpm이 설치되어 있지 않습니다. setup.bat을 먼저 실행해주세요.
    pause
    exit /b 1
)

:: 프론트엔드 실행 (새 창^)
echo [2/2] 프론트엔드 서버 시작 (port 3000^)...
cd frontend
start "ChatBook Frontend" cmd /c "pnpm dev"

cd ..

echo.
echo ======================================
echo   실행 완료!
echo   백엔드: http://127.0.0.1:8000
echo   프론트엔드: http://localhost:3000
echo   (브라우저가 곧 열립니다...^)
echo ======================================

:: 브라우저 열기
timeout /t 5 /nobreak >nul
start http://localhost:3000

pause
