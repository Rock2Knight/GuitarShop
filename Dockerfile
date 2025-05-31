FROM python:3.12.9-alpine3.21

COPY . /python

WORKDIR /python

RUN pip3 install -r requirements.txt && \
    apk add --no-cache bash && \
    wget -O /wait-for-it.sh https://github.com/vishnubob/wait-for-it/raw/master/wait-for-it.sh && \
    chmod +x /wait-for-it.sh

CMD ["sh", "-c", "/wait-for-it.sh postgres:5433 -- alembic upgrade head && python3 main.py"]