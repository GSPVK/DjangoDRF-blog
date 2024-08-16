FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/opt/poetry
ENV POETRY_CACHE_DIR=/opt/.cache
ENV PATH="${POETRY_HOME}/bin:$PATH"

ARG APP_HOME=/app

WORKDIR ${APP_HOME}

# install packages
RUN apk add --no-cache gcc g++ musl-dev curl libffi-dev \
    postgresql-dev zlib-dev jpeg-dev freetype-dev

# install poetry to manage python dependencies
COPY docker/scripts/install-poetry.py /scripts/install-poetry.py
RUN python3 /scripts/install-poetry.py --version ${POETRY_VERSION}

# install dependencies
COPY ./pyproject.toml ./poetry.lock ${APP_HOME}
RUN poetry install --no-interaction --no-ansi

# copy project
COPY . .
