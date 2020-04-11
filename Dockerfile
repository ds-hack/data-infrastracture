FROM python:3.7.6-slim-buster

WORKDIR /usr/src/app

# パッケージマネージャとして、Poetryを採用
COPY poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry config virtualenvs.create false \
  && poetry install

# DBなど他のコンテナとの疎通確認に使用する(pingコマンド)
# 不要になったら削除
RUN apt-get update && apt-get install -y iputils-ping

COPY alembic.ini ./
COPY alembic/ ./alembic
COPY src/ ./src