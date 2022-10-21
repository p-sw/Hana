FROM python:3.10.7
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=hitomi_client.settings.prod

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

COPY ./docker-entrypoint.sh /app/

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 5002

ENTRYPOINT ["/app/docker-entrypoint.sh"]