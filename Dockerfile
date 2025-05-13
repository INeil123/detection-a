FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装buildozer
RUN pip3 install --upgrade pip
RUN pip3 install buildozer

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 构建APK
CMD ["buildozer", "android", "debug"] 