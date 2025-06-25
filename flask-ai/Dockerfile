# 1. Use a slim Python base image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set the working directory
WORKDIR /app

# 4. Install system dependencies (gunicorn may need gcc & others)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# 6. Copy app source code
COPY . .

# 7. Expose Flask port
EXPOSE 5001

# 8. Start the Flask app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
