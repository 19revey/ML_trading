FROM python:3.10-slim
WORKDIR /app
COPY . /app

EXPOSE 8501


RUN apt-get update -y && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt