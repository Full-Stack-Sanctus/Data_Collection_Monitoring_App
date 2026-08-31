FROM python:3.13-slim

# Prevent Python from writing .pyc files
# and ensure logs are immediately visible.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required by psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq5 \
    && rm -rf /var/lib/apt/lists/*

# FIXED: Copy the dependency file out of the backend directory explicitly
COPY backend/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# FIXED: Copy the application source from the backend subfolder into /app
COPY backend/app ./app

# FIXED: Configure your PYTHONPATH so Python knows exactly where to load your 'app' module
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8000

# FIXED: Start FastAPI using Uvicorn with the corrected application import path
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
