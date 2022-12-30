FROM python:3.11-slim

ENV PATH=$PATH:/root/.local/bin
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VERSION=1.3.1

RUN apt-get update \
    && apt-get install -y curl gcc git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python -
