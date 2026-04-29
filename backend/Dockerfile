FROM python:3.12-slim
WORKDIR /app

# 시스템 의존성 (healthcheck용 curl)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드
COPY app/ /app/app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
