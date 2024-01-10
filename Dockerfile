FROM python:3.11.7-bookworm

ENV PYTHONUNBUFFERED=1 POETRY_VERSION=1.6.1

ENV PATH="/root/.local/bin:$PATH"

RUN apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 -

COPY poetry.lock pyproject.toml /rates_app/

WORKDIR /rates_app

RUN poetry config virtualenvs.create false  \
    && poetry install --no-interaction --no-ansi

COPY . /rates_app
