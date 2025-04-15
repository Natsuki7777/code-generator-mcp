FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
  uv pip install --system -e .

# Copy the application code
COPY file_reader_server.py .

# Set the entrypoint
ENTRYPOINT ["python", "file_reader_server.py"]