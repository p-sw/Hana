FROM python:3.10.7-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=hitomi_client.settings.prod

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --system --deploy

COPY . /app/

RUN chmod +x /app/docker-entrypoint.sh

RUN adduser -u 5678 --disable-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 5003

CMD ["/app/docker-entrypoint.sh"]