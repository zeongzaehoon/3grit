# 베이스 이미지로 Python 3.11 사용
FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# 애플리케이션 소스 코드 복사
COPY . /app

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements/requirements.txt

# 코드 작업 디렉토리 설정
WORKDIR /app/src

# PYTHONPATH 설정
ENV PYTHONPATH=/app/src

# 8000번 포트 열기
EXPOSE 8000

# Uvicorn을 사용하여 FastAPI 애플리케이션 실행
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]