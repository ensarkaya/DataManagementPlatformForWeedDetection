# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /usr/src/app

# Install GDAL dependencies
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    python3-gdal \ 
    postgresql-client

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
