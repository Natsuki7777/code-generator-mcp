FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    exiftool \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app


# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv
RUN uv pip install --system -e .

# Install Playwright browsers
RUN python -m playwright install chromium --with-deps

# アプリケーションコードのコピー
COPY main.py .
COPY static ./static

# ポートの指定
EXPOSE 8000

# アプリケーションの起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]