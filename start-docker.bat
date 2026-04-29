@echo off
chcp 65001 >nul
title ChatBook - Docker 실행 중...

echo ============================================
echo          ChatBook Docker 실행
echo ============================================
echo 실행 모드를 선택하세요:
echo   [1] 데모 모드 (API 키 없이 체험)
echo   [2] 일반 모드 (실제 AI 사용)
echo   [Q] 종료
echo.

cd /d "%~dp0"

:MODE_SELECT
set /p "MODE=선택 (1/2/Q): "

if /i "%MODE%"=="1" goto MODE_DEMO
if /i "%MODE%"=="2" goto MODE_NORMAL
if /i "%MODE%"=="Q" goto MODE_QUIT
echo [오류] 잘못된 입력입니다. 1, 2, Q 중에서 선택하세요.
echo.
goto MODE_SELECT

:MODE_QUIT
echo.
echo ChatBook을 종료합니다.
pause
exit /b 0

:MODE_DEMO
echo.
echo [데모 모드] API 키 없이 체험 모드로 실행합니다.
if not exist ".env" (
    echo .env 파일이 없습니다. .env.example에서 복사합니다.
    copy .env.example .env >nul
)
powershell -Command "(Get-Content .env) -replace 'USE_DEMO_MODE=.*', 'USE_DEMO_MODE=true' | Set-Content .env"
echo USE_DEMO_MODE=true 로 설정되었습니다.
goto DOCKER_CHECK

:MODE_NORMAL
echo.
echo [일반 모드] 실제 AI API 키가 필요합니다.
if not exist ".env" (
    echo .env 파일이 없습니다. .env.example에서 복사합니다.
    copy .env.example .env >nul
)
powershell -Command "(Get-Content .env) -replace 'USE_DEMO_MODE=.*', 'USE_DEMO_MODE=false' | Set-Content .env"
echo USE_DEMO_MODE=false 로 설정되었습니다.
echo.
echo 일반 모드에서는 실제 AI API 키가 필요합니다.
echo .env 파일을 열어 다음 항목을 입력하세요:
echo   OPENAI_API_KEY=sk-your-key
echo   GEMINI_API_KEY=your-key
echo   DEEPSEEK_API_KEY=your-key
echo.

:API_KEY_PROMPT
set /p "API_KEY_INPUT=API 키를 지금 입력하시겠습니까? (Y/N): "
if /i "%API_KEY_INPUT%"=="Y" (
    echo .env 파일을 메모장으로 엽니다.
    notepad .env
    echo.
    echo API 키 입력 후 메모장을 닫고 아무 키나 누르면 계속 진행합니다...
    pause >nul
    goto DOCKER_CHECK
)
if /i "%API_KEY_INPUT%"=="N" (
    echo API 키 입력을 건너뜁니다. 나중에 .env 파일을 직접 수정하세요.
    goto DOCKER_CHECK
)
echo [오류] 잘못된 입력입니다. Y 또는 N을 입력하세요.
goto API_KEY_PROMPT

:DOCKER_CHECK
echo.
echo Docker 데몬 상태 확인 중...
:: Docker 실행 확인
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Docker가 설치되어 있지 않습니다.
    echo Docker Desktop을 설치해주세요: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker info >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Docker 데몬이 실행 중이지 않습니다.
    echo Docker Desktop을 먼저 실행해주세요.
    pause
    exit /b 1
)

echo Docker 데몬이 정상 실행 중입니다.
echo.

echo [1/2] Docker 이미지 빌드 중...
docker compose build
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Docker 이미지 빌드에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo [2/2] Docker 컨테이너 실행 중...
docker compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Docker 컨테이너 실행에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo ======================================
echo   Docker 실행 완료!
echo   백엔드: http://localhost:8000
echo   프론트엔드: http://localhost:3000
echo   (브라우저가 곧 열립니다...^)
echo.
echo   종료: docker compose down
echo ======================================

:: 브라우저 열기
timeout /t 5 /nobreak >nul
start http://localhost:3000

pause
