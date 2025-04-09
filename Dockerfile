FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
# uv를 사용하는 경우:
# RUN pip install uv && uv sync --no-dev
# pip를 사용하는 경우:
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# 컨테이너 실행 시 필요한 인자(--API_KEY 등)는 docker run 명령어 뒤에 추가합니다.
ENTRYPOINT ["python", "server.py"] 