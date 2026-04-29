@echo off
chcp 65001 >nul
title ChatBook - Docker 환경 초기화

echo ============================================
echo          ChatBook Docker 환경 초기화
echo ============================================
echo 경고: 이 작업은 Docker로 생성된 모든 파일을 삭제합니다!
echo - Docker 컨테이너 (chatbook-backend, chatbook-frontend)
echo - Docker 이미지
echo - Docker 볼륨
echo - SQLite 데이터베이스 파일 (./data/)
echo.

cd /d "%~dp0"

set /p "CONFIRM=계속하시겠습니까? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo 작업이 취소되었습니다.
    pause
    exit /b 0
)

echo.
echo [1/5] Docker 컨테이너 중지 및 삭제 중...
docker compose down -v 2>nul
echo   컨테이너 및 볼륨 삭제 완료

echo.
echo [2/5] Docker 이미지 삭제 중...
for /f "usebackq delims=" %%i in (`docker compose images -q 2^>nul`) do (
    docker rmi %%i 2>nul
)
echo   이미지 삭제 완료 (없는 경우 무시)

echo.
echo [3/5] SQLite 데이터베이스 파일 삭제 중...
if exist "data" (
    for %%f in ("data\*") do (
        if /i not "%%~nxf"==".gitkeep" (
            del /q "%%f" 2>nul
            echo   %%f 삭제됨
        )
    )
)
echo   data\ 디렉토리 정리 완료 (.gitkeep 보존)

echo.
echo [4/5] 프론트엔드 빌드 아티팩트 삭제 중...
if exist "frontend\.next" (
    rmdir /s /q "frontend\.next" 2>nul
    echo   frontend\.next\ 삭제 완료
) else (
    echo   frontend\.next\ 없음 (건너뜀)
)

echo.
echo [5/5] dangling 이미지 정리 중...
docker image prune -f 2>nul
echo   dangling 이미지 정리 완료

echo.
echo ============================================
echo   Docker 환경 초기화 완료!
echo   - 모든 Docker 리소스가 삭제되었습니다.
echo   - 데이터베이스 파일이 초기화되었습니다.
echo.
echo   이제 start-docker.bat을 실행하여 다시 시작할 수 있습니다.
echo ============================================
pause
