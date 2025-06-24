# 1. Use Python as the base image
FROM python:3.10

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy all files from your local flask-ai/ folder to the container
COPY . .

# 4. Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5. Expose the port Flask runs on
EXPOSE 5001

# 6. Run the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
