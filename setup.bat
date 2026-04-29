@echo off
:: 1. 한글 깨짐 방지를 위해 코드 페이지를 UTF-8로 설정합니다.
chcp 65001 >nul
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0"
set "RUNTIME_DIR=%ROOT_DIR%runtime"
set "PYTHON_DIR=%RUNTIME_DIR%\python"
set "NODE_DIR=%RUNTIME_DIR%\node"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.4/python-3.12.4-embed-amd64.zip"
set "NODE_URL=https://nodejs.org/dist/v20.12.2/node-v20.12.2-win-x64.zip"

echo ==================================================
echo    Chatbook 환경 설정을 시작합니다 (인코딩: UTF-8)
echo ==================================================

:: 2. 폴더 생성 및 권한 체크
if not exist "%RUNTIME_DIR%" (
    mkdir "%RUNTIME_DIR%"
    if !errorlevel! neq 0 (
        echo [에러] 폴더 생성 권한이 없습니다. 관리자 권한으로 실행해 보세요.
        pause & exit /b
    )
)

:: 3. Python 설치 섹션
echo [1/6] Portable Python 체크 중...
if not exist "%PYTHON_DIR%\python.exe" (
    echo - Python 다운로드 중... (용량이 커서 시간이 걸릴 수 있습니다)
    powershell -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%RUNTIME_DIR%\python.zip' } catch { Write-Error '다운로드 실패'; exit 1 }"
    if !errorlevel! neq 0 ( pause & exit /b )

    echo - 압축 해제 중...
    powershell -Command "Expand-Archive -Path '%RUNTIME_DIR%\python.zip' -DestinationPath '%PYTHON_DIR%' -Force"
    del "%RUNTIME_DIR%\python.zip"

    :: 임베디드 파이썬 환경 설정 필수 단계
    echo - pip 설치를 위한 데이터 준비...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_DIR%\get-pip.py'"
    "%PYTHON_DIR%\python.exe" "%PYTHON_DIR%\get-pip.py" --no-warn-script-location
    
    (
        echo python312.zip
        echo .
        echo import site
    ) > "%PYTHON_DIR%\python312._pth"
    del "%PYTHON_DIR%\get-pip.py"
) else (
    echo - Python이 이미 설치되어 있습니다.
)

:: 4. Node.js 설치 섹션
echo.
echo [2/6] Portable Node.js 체크 중...
if not exist "%NODE_DIR%\node.exe" (
    echo - Node.js 다운로드 중...
    powershell -Command "Invoke-WebRequest -Uri '%NODE_URL%' -OutFile '%RUNTIME_DIR%\node.zip'"
    
    echo - 압축 해제 중...
    powershell -Command "Expand-Archive -Path '%RUNTIME_DIR%\node.zip' -DestinationPath '%RUNTIME_DIR%\node_temp' -Force"
    
    for /d %%i in ("%RUNTIME_DIR%\node_temp\node-*") do move "%%i" "%NODE_DIR%" >nul
    rmdir /s /q "%RUNTIME_DIR%\node_temp"
    del "%RUNTIME_DIR%\node.zip"
    
    echo - Corepack (pnpm^) 활성화 중...
    :: 글로벌 경로 오염 방지를 위해 설치 경로를 포터블 Node 디렉토리로 명시합니다.
    call "%NODE_DIR%\corepack.cmd" enable --install-directory "%NODE_DIR%" pnpm
) else (
    echo - Node.js가 이미 설치되어 있습니다.
    if not exist "%NODE_DIR%\pnpm.cmd" (
        echo - Corepack (pnpm^) 활성화 중...
        call "%NODE_DIR%\corepack.cmd" enable --install-directory "%NODE_DIR%" pnpm
    )
)

:: 5. 환경 변수 적용 (현재 창 한정)
echo.
echo [3/6] 환경 변수 적용...
set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%NODE_DIR%;%PATH%"

:: .env 파일 자동 생성 (.env.example → .env)
if not exist "%ROOT_DIR%.env" (
    if exist "%ROOT_DIR%.env.example" (
        copy "%ROOT_DIR%.env.example" "%ROOT_DIR%.env" >nul
        echo   [INFO] .env.example 파일을 .env로 복사했습니다.
        echo   [INFO] .env 파일을 열어 API 키를 실제 값으로 수정해주세요.
    )
)

:: 프론트엔드 전용 .env.local 파일 자동 생성 (NEXT_PUBLIC_API_URL)
if not exist "%ROOT_DIR%frontend\.env.local" (
    (
        echo # 프론트엔드 전용 환경변수
        echo # Next.js가 자동으로 로드하며, 백엔드에는 영향을 주지 않습니다.
        echo.
        echo # 백엔드 API URL ^(브라우저에서 직접 접근, SSE 스트리밍용^)
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
    ) > "%ROOT_DIR%frontend\.env.local"
    echo   [INFO] frontend/.env.local 파일을 생성했습니다. ^(NEXT_PUBLIC_API_URL=http://localhost:8000^)
    echo   [INFO] Docker 배포 시에는 docker-compose.yml의 build args로 자동 주입됩니다.
)

:: 6. 백엔드 라이브러리 설치
echo.
echo [4/6] 백엔드 패키지 설치 (pip)...
if exist "%ROOT_DIR%backend\requirements.txt" (
    "%PYTHON_DIR%\python.exe" -m pip install --upgrade pip
    "%PYTHON_DIR%\python.exe" -m pip install -r "%ROOT_DIR%backend\requirements.txt"
) else (
    echo   [^^!] 경고: backend\requirements.txt를 찾을 수 없습니다.
)

:: 7. 프론트엔드 패키지 설치
echo.
echo ========================================
echo   [5/6] 프론트엔드 패키지 설치 중...
echo ========================================
echo.

cd /d "%ROOT_DIR%frontend"

REM 기존 node_modules 정리
if exist "node_modules" (
    echo   기존 node_modules 정리 중...
    rmdir /s /q "node_modules"
)

echo   pnpm install 실행 중...
call pnpm install

if %errorlevel% neq 0 (
    echo   [^^!] 프론트엔드 패키지 설치 실패
    pause
    exit /b 1
)
echo   프론트엔드 패키지 설치 완료.

cd /d "%ROOT_DIR%"

:: 8. 완료
echo.
echo [6/6] 환경 설정 완료
echo.
echo ==================================================
echo    Chatbook 환경 설정이 완료되었습니다!
echo    이제 start.bat을 실행하여 앱을 시작할 수 있습니다.
echo ==================================================
echo.
pause
exit /b 0
