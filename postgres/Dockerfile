FROM postgres:17-alpine

ENV POSTGRES_USER root  
ENV POSTGRES_PASSWORD 1234
ENV POSTGRES_DB 3grit

# 초기 DB 스키마 설치
# sql 파일이 여러개 있을 경우, alpha-numeric 순으로 처리됨.
# COPY *.sql /docker-entrypoint-initdb.d/

EXPOSE 5432