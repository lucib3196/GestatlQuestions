# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.13.7
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --uid "${UID}" \
    appuser \
    && mkdir -p /home/appuser \
    && chown -R appuser:appuser /home/appuser
# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.

# Install system dependencies (e.g., for OpenCV)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*


# Install Poetry
RUN pip install --no-cache-dir poetry

# Copyt dependencies
COPY backend/pyproject.toml backend/poetry.lock* ./ 



# Configure Poetry and install dependencies 
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy the source code into the container.
COPY backend/ ./backend

# Expose the port that the application listens on.
EXPOSE 8000

## Notes: Depending on implementation changing the workdir to base app might prevent
## Needigng to copy the frontend folder but it should be fine for now
WORKDIR /app/backend

ENV PYTHONPATH=/app/backend
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


