#!/bin/bash
# Docker 통합 테스트 스크립트
set -e

echo "🏗️ Docker Compose 빌드 및 시작..."
docker compose up -d --build

echo "⏳ 서비스 초기화 대기 (15초)..."
sleep 15

echo ""
echo "🔍 1. Backend Health Check"
if curl -sf http://localhost:8000/api/health > /dev/null; then
  echo "   ✅ Backend health check passed"
else
  echo "   ❌ Backend health check failed"
  exit 1
fi

echo ""
echo "🔍 2. Frontend 접근 확인"
if curl -sf http://localhost:3000 > /dev/null; then
  echo "   ✅ Frontend is accessible"
else
  echo "   ❌ Frontend is not accessible"
  exit 1
fi

echo ""
echo "🔍 3. API Models Endpoint"
if curl -sf http://localhost:8000/api/models | grep -q "demo"; then
  echo "   ✅ Models endpoint returns demo provider"
else
  echo "   ❌ Models endpoint failed"
  exit 1
fi

echo ""
echo "🔍 4. CORS Headers 확인"
CORS=$(curl -s -I -X OPTIONS \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  http://localhost:8000/api/models 2>&1)
if echo "$CORS" | grep -qi "access-control"; then
  echo "   ✅ CORS headers present"
else
  echo "   ⚠️  CORS headers not detected (may still work)"
fi

echo ""
echo "🔍 5. Conversations API"
CONV=$(curl -sf http://localhost:8000/api/conversations)
if echo "$CONV" | grep -q "id"; then
  echo "   ✅ Conversations API works"
  COUNT=$(echo "$CONV" | grep -o '"id"' | wc -l)
  echo "   📊 Seed conversations: $COUNT"
else
  echo "   ❌ Conversations API failed"
  exit 1
fi

echo ""
echo "✅ 모든 통합 테스트 통과!"
