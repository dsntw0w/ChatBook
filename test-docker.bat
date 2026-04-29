@echo off
chcp 65001 >nul
echo Docker 통합 테스트 시작...

echo [1/5] Backend Health Check...
curl -sf http://localhost:8000/api/health
IF %ERRORLEVEL% NEQ 0 (
  echo ❌ Backend health check failed
  exit /b 1
)
echo ✅ Backend OK

echo [2/5] Frontend 접근 확인...
curl -sf http://localhost:3000
IF %ERRORLEVEL% NEQ 0 (
  echo ❌ Frontend not accessible
  exit /b 1
)
echo ✅ Frontend OK

echo [3/5] API Models 확인...
curl -sf http://localhost:8000/api/models
IF %ERRORLEVEL% NEQ 0 (
  echo ❌ Models API failed
  exit /b 1
)
echo ✅ Models API OK

echo [4/5] Conversations API 확인...
curl -sf http://localhost:8000/api/conversations
IF %ERRORLEVEL% NEQ 0 (
  echo ❌ Conversations API failed
  exit /b 1
)
echo ✅ Conversations API OK

echo [5/5] Orders API 확인...
curl -sf http://localhost:8000/api/orders
IF %ERRORLEVEL% NEQ 0 (
  echo ❌ Orders API failed
  exit /b 1
)
echo ✅ Orders API OK

echo ✅ 모든 통합 테스트 통과!
