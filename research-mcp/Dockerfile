FROM python:3.13-slim

# Install file type detection library
RUN apk add --no-cache gcc musl-dev linux-headers

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv
RUN uv pip install --system -e .

# Copy the application code
COPY server.py .

# Set the entrypoint
ENTRYPOINT ["python", "server.py"]