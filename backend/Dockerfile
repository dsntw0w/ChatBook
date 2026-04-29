FROM python:3.12.8-slim
WORKDIR /app

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드
COPY app/ /app/app/

# non-root 사용자 생성 및 권한 설정 (Frontend와 일관된 uid/gid 1001)
RUN addgroup --system --gid 1001 python && \
    adduser --system --uid 1001 --gid 1001 python && \
    mkdir -p /app/data && \
    chown -R python:python /app

USER python

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
