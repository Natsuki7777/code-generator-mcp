FROM python:3.13-slim

# Install file type detection library
RUN apt-get update && apt-get install -y libmagic1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
  uv pip install --system -e .


# Copy the application code
COPY code_structure_server.py .

# Set the entrypoint
ENTRYPOINT ["python", "code_structure_server.py"]