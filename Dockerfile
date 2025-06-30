FROM python:3.12.9-alpine3.21

WORKDIR /app

COPY requirements.txt .
RUN pip3 cache purge && \
    pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk add --no-cache bash && \
    wget -O /wait-for-it.sh https://github.com/vishnubob/wait-for-it/raw/master/wait-for-it.sh && \
    chmod +x /wait-for-it.sh

COPY . .
ENV ALEMBIC_CONFIG=/app/app/migration/alembic.ini
ENV PYTHONPATH=/app

CMD ["sh", "-c", "/wait-for-it.sh postgres:5433 -- alembic upgrade head && python3 -u ./app/main.py"]