FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY movies/ ./movies/
COPY config/ ./config/
COPY manage.py .
COPY IMDB_Top_1000_Movies.csv .

ENV PYTHONUNBUFFERED=1

# 8000 is used for local development and plain `docker run`. Render (and
# similar platforms) inject their own PORT env var at runtime and expect
# the app to bind to that instead, the shell form below picks it up if
# present and falls back to 8000 if not.
EXPOSE 8000

# Migrations and the catalog load run every container start. This is
# idempotent (populate_movies clears and reloads the table) and cheap at
# this dataset size. Note: without a mounted persistent volume, the
# SQLite file lives inside the container's writable layer, it survives an
# in-process restart but not a full container recreation (e.g. a Render
# free-tier redeploy). That's an intentional scope cut for a demo project,
# not an oversight, a real deployment would move to a persistent disk or
# a hosted Postgres instance instead.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py populate_movies && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
