# 베이스 이미지로 Python 3.11 사용
FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# 애플리케이션 소스 코드 복사
COPY . /app

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r /app/requirements.txt

# Uvicorn을 사용하여 FastAPI 애플리케이션 실행
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app"]