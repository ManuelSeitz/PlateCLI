FROM python:3.14-slim

ARG UID=1000
ARG GID=1000

WORKDIR /app

RUN apt-get update && apt-get install -y \ 
    wget \
    gnupg \
    unzip \ 
    git \
    git-flow \
    chromium \
    chromium-driver \
    build-essential\
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN groupadd -g ${GID} python && \
    useradd -u ${UID} -g ${GID} -m python

COPY --chown=python:python . .

RUN chown -R python:python /app

USER python
ENV HOME=/home/python

RUN uv sync --locked

EXPOSE 8000