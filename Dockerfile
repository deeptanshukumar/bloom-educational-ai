FROM python:3.11-slim-buster

WORKDIR /app

COPY backend/requirements.txt requirements.txt

# Install build dependencies, including gcc and zlib development files
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app.py /app/
COPY backend/config.py /app/
COPY backend/init_db.py /app/
COPY backend/test_db.py /app/
COPY backend/models /app/models
COPY backend/routes /app/routes
COPY backend/scripts /app/scripts
COPY backend/services /app/services
COPY backend/uploads /app/uploads
COPY backend/utils /app/utils

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]