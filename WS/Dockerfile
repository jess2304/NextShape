# Stage 1: build the Vue frontend. Its tests run first: a failing test stops the build.
FROM node:20-alpine AS frontend
WORKDIR /app/UI

COPY UI/package*.json ./
RUN npm ci
COPY UI/ ./

# Vite writes the API URL into the bundle at build time.
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm test && npm run build

# Stage 2: the Django backend, with the built frontend served by WhiteNoise.
FROM python:3.11-slim AS backend
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Security updates of the base image.
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Dependencies before the code: editing the code keeps this layer cached.
COPY WS/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY WS/ ./

COPY --from=frontend /app/UI/dist ./UI/dist

EXPOSE 8000

# Stage 3: the production image.
FROM backend AS production

# collectstatic only reads the settings: a placeholder secret is enough at build time.
RUN DJANGO_SECRET_KEY=build-time-placeholder ENV=test python manage.py collectstatic --noinput

# The hosting platform may set PORT; 8000 otherwise.
CMD ["sh", "-c", "gunicorn next_shape_ws.wsgi:application --bind 0.0.0.0:${PORT:-8000} --access-logfile - --error-logfile -"]
