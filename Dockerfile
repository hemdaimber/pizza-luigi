# Use a base image with Python 2.7
FROM python:2.7

# Install MariaDB development libraries
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the necessary port
EXPOSE 8080

# Command to run the application
CMD ["python", "pizza_site.py"]
