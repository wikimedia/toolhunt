FROM python:3.9 as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.9

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

CMD ["flask", "--debug", "run", "--host", "0.0.0.0"]

# COPY ./compose/local/flask/entrypoint /entrypoint
# RUN sed -i 's/\r$//g' /entrypoint
# RUN chmod +x /entrypoint

#COPY ./compose/local/flask/start /start
#RUN sed -i 's/\r$//g' /start
#RUN chmod +x /start

#ENTRYPOINT ["/start"]
