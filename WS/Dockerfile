# Build frontend
FROM node:20-alpine AS frontend
WORKDIR /app/UI

COPY UI/package*.json ./
RUN npm ci
COPY UI/ ./

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Build backend
FROM python:3.11-slim AS backend
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

COPY WS/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY WS/ ./

COPY --from=frontend /app/UI/dist ./UI/dist

EXPOSE 8000

# Test image
FROM backend AS test

COPY WS/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Production image
FROM backend AS production

CMD ["sh", "-c", "gunicorn next_shape_ws.wsgi:application --bind 0.0.0.0:${PORT:-8000} --access-logfile - --error-logfile -"]
