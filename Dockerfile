FROM python:3.11-slim

WORKDIR /app/

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV PYTHONPATH=/app

COPY ./app ./app

COPY ./alembic.ini /app/

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info"]
