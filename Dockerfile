FROM python:3.11-slim-buster
WORKDIR /app
COPY backend/uploads /app/uploads
CMD ["echo", "Uploads directory test successful"]