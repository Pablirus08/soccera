FROM python:3.11-slim

WORKDIR /app

# libpq needed for psycopg at runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ ./src/
COPY alembic.ini ./
COPY scripts/ ./scripts/

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1

CMD ["python", "scripts/run_live_poll.py"]
