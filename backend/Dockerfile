FROM python:3.12-slim-bullseye

WORKDIR /app

# Install build dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc

# Copy only requirements file first to leverage Docker cache.
COPY requirements.txt .

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . /app

# Install the application.
RUN pip install --no-cache-dir .

EXPOSE 8000

# Run the application.
CMD ["nlpanno", "start-annotation"]
