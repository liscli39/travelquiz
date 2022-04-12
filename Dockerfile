FROM python:3.9.6-buster

# Pythonの出力バッファリングを無効化
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリ作成
WORKDIR /app

RUN apt-get update && apt-get -y install gdal-bin libgdal-dev

# PyPIパッケージのインストール
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# 必要なファイルのみコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# .envファイルの読み込みを無効化
ENV DJANGO_READ_ENV_FILE=False
