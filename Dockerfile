FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

ENV PYTHONUNBUFFERED=1

COPY alembic.ini .
COPY alembic/ alembic/
COPY app/ app/
COPY data/ data/
COPY scripts/ scripts/
COPY eval/ eval/
COPY tests/ tests/
COPY pytest.ini .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
