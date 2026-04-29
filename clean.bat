@echo off
chcp 65001 >nul
title Chatbook - 초기화

echo ========================================
echo   Chatbook 공장 초기화
echo ========================================
echo.
echo   [!] 경고: 이 작업은 모든 데이터와
echo       포터블 환경을 삭제합니다!
echo.
echo   삭제 대상:
echo     - runtime\ (포터블 Python)
echo     - *.db (데이터베이스 파일)
echo     - .env (API 키 설정 파일)
echo     - frontend\.env.local (프론트엔드 환경변수)
echo     - __pycache__ 및 .pyc/.pyo 파일
echo     - .pytest_cache, .egg-info 폴더
echo     - .pnpm-store (pnpm 패키지 캐시)
echo     - frontend\node_modules
echo     - frontend\.next
echo     - 로그 파일
echo     - OS 임시 파일 (.DS_Store, Thumbs.db)
echo.
echo   보존 대상:
echo     - 소스 코드 (.py, .tsx, .ts 등)
echo     - .env.example, requirements.txt
echo     - package.json, pnpm-lock.yaml
echo.

set /p "CONFIRM=계속하시겠습니까? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo 취소되었습니다.
    pause
    exit /b 0
)

set "PROJECT_DIR=%~dp0"

echo.
echo [0/8] 실행 중인 프로세스 종료 중...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo   프로세스 종료 완료 (파일 잠금 해제 대기)

echo.
echo [1/8] 포터블 Python 환경 삭제 중...
if exist "%PROJECT_DIR%runtime" (
    attrib -r /s /d "%PROJECT_DIR%runtime\*" >nul 2>&1
    rmdir /s /q "%PROJECT_DIR%runtime"
    echo   runtime\ 삭제 완료
) else (
    echo   runtime\ 없음 (건너뜀)
)

echo.
echo [2/8] 데이터베이스 파일 삭제 중...
set "DB_DELETED="
if exist "%PROJECT_DIR%backend\app\data\*.db" (
    del /q "%PROJECT_DIR%backend\app\data\*.db"
    echo   backend\app\data\ DB 파일 삭제 완료
    set "DB_DELETED=1"
)
if exist "%PROJECT_DIR%backend\*.db" (
    del /q "%PROJECT_DIR%backend\*.db"
    echo   backend\ DB 파일 삭제 완료
    set "DB_DELETED=1"
)
if exist "%PROJECT_DIR%*.db" (
    del /q "%PROJECT_DIR%*.db"
    echo   루트 DB 파일 삭제 완료
    set "DB_DELETED=1"
)
if not defined DB_DELETED (
    echo   DB 파일 없음 (건너뜀)
)

echo.
echo [3/8] Python 캐시 및 빌드 아티팩트 삭제 중...
REM __pycache__ 디렉토리
for /f "delims=" %%d in ('dir /s /b /ad "%PROJECT_DIR%__pycache__" 2^>nul') do (
    rmdir /s /q "%%d" 2>nul
    echo   %%d 삭제됨
)
REM 독립형 .pyc / .pyo 파일
del /s /q "%PROJECT_DIR%*.pyc" 2>nul
del /s /q "%PROJECT_DIR%*.pyo" 2>nul
REM .pytest_cache
if exist "%PROJECT_DIR%.pytest_cache" rmdir /s /q "%PROJECT_DIR%.pytest_cache" 2>nul
if exist "%PROJECT_DIR%backend\.pytest_cache" rmdir /s /q "%PROJECT_DIR%backend\.pytest_cache" 2>nul
REM .egg-info 디렉토리
for /f "delims=" %%d in ('dir /s /b /ad "%PROJECT_DIR%*.egg-info" 2^>nul') do (
    rmdir /s /q "%%d" 2>nul
    echo   %%d 삭제됨
)
echo   Python 캐시 삭제 완료

echo.
echo [4/8] Frontend 빌드/모듈 삭제 중...
if exist "%PROJECT_DIR%frontend\node_modules" (
    rmdir /s /q "%PROJECT_DIR%frontend\node_modules"
    echo   node_modules\ 삭제 완료
) else (
    echo   node_modules\ 없음 (건너뜀)
)
if exist "%PROJECT_DIR%frontend\.next" (
    rmdir /s /q "%PROJECT_DIR%frontend\.next"
    echo   .next\ 삭제 완료
) else (
    echo   .next\ 없음 (건너뜀)
)
if exist "%PROJECT_DIR%.pnpm-store" (
    rmdir /s /q "%PROJECT_DIR%.pnpm-store"
    echo   .pnpm-store\ 삭제 완료
) else (
    echo   .pnpm-store\ 없음 (건너뜀)
)
REM pnpm-lock.yaml은 재현 가능한 빌드를 위해 유지 (git 커밋 대상)
echo   pnpm-lock.yaml 유지 (재현 가능한 빌드)
echo   Frontend 정리 완료

echo.
echo [5/8] .env 파일 삭제 중...
if exist "%PROJECT_DIR%.env" (
    del /q "%PROJECT_DIR%.env"
    echo   .env 삭제 완료 (API 키 정보 제거)
) else (
    echo   .env 없음 (건너뜀)
)
if exist "%PROJECT_DIR%frontend\.env.local" (
    del /q "%PROJECT_DIR%frontend\.env.local"
    echo   frontend\.env.local 삭제 완료 (프론트엔드 환경변수)
) else (
    echo   frontend\.env.local 없음 (건너뜀)
)

echo.
echo [6/8] 로그 파일 삭제 중...
del /s /q "%PROJECT_DIR%*.log" 2>nul
echo   로그 파일 삭제 완료

echo.
echo [7/8] OS 임시 파일 삭제 중...
del /s /q "%PROJECT_DIR%.DS_Store" 2>nul
del /s /q "%PROJECT_DIR%Thumbs.db" 2>nul
echo   OS 임시 파일 삭제 완료

echo.
echo [8/8] 빈 data 디렉토리 정리 중...
REM data/ 디렉토리 내 모든 파일 삭제 후 .gitkeep 복원
if exist "%PROJECT_DIR%data" (
    del /s /q "%PROJECT_DIR%data\*" 2>nul
    for /f "delims=" %%d in ('dir /s /b /ad "%PROJECT_DIR%data" 2^>nul') do rmdir /s /q "%%d" 2>nul
    echo . > "%PROJECT_DIR%data\.gitkeep"
    echo   data\ 디렉토리 정리 완료 (.gitkeep 복원)
)

echo.
echo ========================================
echo   초기화 완료!
echo ========================================
echo.
echo   setup.bat을 실행하여 환경을 다시 구성할 수 있습니다.
echo.
pause
