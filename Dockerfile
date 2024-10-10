# syntax=docker/dockerfile:1

# Use a specific Python version (specified as an ARG for flexibility)
ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files and sets unbuffered mode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Create a non-privileged user to run the app
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy only requirements.txt to take advantage of Docker caching for dependencies
COPY requirements.txt .

# Install dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user created earlier
USER appuser

# Copy the entire source code into the container
COPY . .

# Expose the port your application will run on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
