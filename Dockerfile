FROM python:3.11-slim-buster

WORKDIR /app

COPY backend/requirements.txt requirements.txt

# Install zlib development files (and other potentially useful build dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY backend .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]