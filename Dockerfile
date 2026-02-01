# First, build the application in the `/app` directory.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Enable bytecode compilation and copy mode for reproducible builds
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Allow Python downloads since we need the specific version
ENV UV_PYTHON_DOWNLOADS=auto

WORKDIR /app

# Install system dependencies needed for building
# build-essential is preferred over gcc/g++ as it's more explicit and includes make.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# First, sync dependencies to leverage Docker cache
# Only run if lock file or pyproject.toml changes
COPY uv.lock pyproject.toml /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Now copy the rest of the application
COPY src /app/src
COPY pyproject.toml /src/pyproject.toml

# Install the project and its dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


# Then, use a final image without uv
FROM python:3.13-slim-bookworm AS production

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Install runtime system dependencies and remove setuid/setgid bits
# The -xdev flag prevents find from scanning pseudo-filesystems like /proc
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && find / -xdev -perm /6000 -type f -exec chmod a-s {} \; \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app/src /app/src
COPY --from=builder --chown=nonroot:nonroot /app/pyproject.toml /app/pyproject.toml

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1

# Use the non-root user to run our application
USER nonroot

# Use `/app` as the working directory
WORKDIR /app

# Run the application by default
CMD ["python", "-m", "src.main"]
