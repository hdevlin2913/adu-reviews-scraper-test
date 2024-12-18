FROM python:3.12.7-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apt-get update -qq -y && \
    apt-get install -y \
      libmagic1 \
      ffmpeg \
      libsm6 \
      libxext6 \
      libgl1 \
      libgl1-mesa-glx \
      unzip \
      libasound2 \
      libatk-bridge2.0-0 \
      libgtk-4-1 \
      libnss3 \
      xdg-utils \
      wget && \
    wget -q -O chrome-linux64.zip https://bit.ly/chrome-linux64-121-0-6167-85 && \
    unzip chrome-linux64.zip && \
    rm chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome/ && \
    ln -s /opt/chrome/chrome /usr/local/bin/ && \
    wget -q -O chromedriver-linux64.zip https://bit.ly/chromedriver-linux64-121-0-6167-85 && \
    unzip -j chromedriver-linux64.zip chromedriver-linux64/chromedriver && \
    rm chromedriver-linux64.zip && \
    mv chromedriver /usr/local/bin/

WORKDIR /app

COPY ./manage.py ./poetry.lock ./pyproject.toml ./README.md ./

RUN pip install poetry && poetry config virtualenvs.create false

COPY scraper ./scraper
COPY scripts ./scripts

RUN poetry install
