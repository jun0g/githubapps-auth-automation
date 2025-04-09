# Dockerfile
FROM python:3.13-alpine

WORKDIR /app

# 기본 도구 설치
RUN apk update && \
    apk add --no-cache \
        build-base \
        curl \
        git \
        binutils \
        zip \
        py3-pip && \
    pip install --upgrade pip && \
    pip install pyinstaller

# 소스 복사
COPY main.py ./ 
COPY utils/* ./utils/

# 의존성 설치
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 빌드
RUN pyinstaller --clean -F main.py --name ghapps-auth

# 컨테이너가 바로 종료되지 않도록 유지 (파일 복사용)
ENTRYPOINT ["sleep", "infinity"]
