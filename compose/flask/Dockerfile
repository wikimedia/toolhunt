FROM python:3.9-slim-bullseye as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.9-slim-bullseye

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN apt-get update && apt-get install -y "build-essential" "default-libmysqlclient-dev" && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

CMD ["flask", "--debug", "run", "--host", "0.0.0.0"]
