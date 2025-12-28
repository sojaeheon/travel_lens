FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN apt-get update \
    && apt-get install -y dos2unix postgresql-client \
    && pip install --no-cache-dir -r requirements.txt \
    && dos2unix /usr/local/bin/entrypoint.sh \
    && chmod +x /usr/local/bin/entrypoint.sh \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["entrypoint.sh"]
CMD ["python","manage.py","runserver","0.0.0.0:8000"]

EXPOSE 8000
