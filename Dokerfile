FROM python:3.8-slim

# curl 모듈 설치
RUN apt-get update && apt-get install -y curl

# 작업 디렉터리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt requirements.txt
COPY app.py app.py

# Flask 설치
RUN pip install -r requirements.txt

# 앱 실행
CMD ["python", "app.py"]
