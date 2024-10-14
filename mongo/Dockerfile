# 베이스 이미지로 MongoDB 공식 이미지를 사용
FROM mongo:7.0

# label for manager
LABEL maintainer="jaehoon@4grit.com"

# set init script
# COPY ./init-mongo.js /docker-entrypoint-initdb.d/

# set env: username, password
ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_ROOT_PASSWORD=1234

# data volume
VOLUME /data/db

# MongoDB port
EXPOSE 27017

# cmd: mongod (MongoDB demon activate cmd)
CMD ["mongod"]