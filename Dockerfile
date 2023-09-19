# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN python -m pip install bcrypt==4.0.1
RUN python -m pip install blinker==1.6.2
RUN python -m pip install click==8.1.7
RUN python -m pip install colorama==0.4.6
RUN python -m pip install Flask==2.3.3
RUN python -m pip install Flask-SQLAlchemy==3.1.1
RUN python -m pip install greenlet==2.0.2
RUN python -m pip install itsdangerous==2.1.2
RUN python -m pip install Jinja2==3.1.2
RUN python -m pip install MarkupSafe==2.1.3
RUN python -m pip install SQLAlchemy==2.0.20
RUN python -m pip install typing_extensions==4.7.1
RUN python -m pip install Werkzeug==2.3.7
 

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD python3 -m flask --app ladder run
