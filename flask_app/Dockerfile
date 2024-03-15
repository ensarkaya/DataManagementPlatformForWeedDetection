# Use an official Python runtime as a parent image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Set the timezone
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    htop \
    nano \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies globally to avoid issues with PATH
RUN pip3 install Werkzeug==2.2.2 \
    Flask==2.0.1 \
    gunicorn==20.0.4 \
    pandas==1.4.1 \
    numpy==1.22.2 \
    albumentations==1.1.0 \
    tqdm==4.64.1 \
    scikit-image==0.19.2 \
    scikit-learn==1.1.3 \
    kornia==0.6.8 \
    matplotlib==3.6.2 \
    patchify==0.2.3 \
    timm==0.6.12 \
    segmentation-models-pytorch==0.3.2 \
    pillow==10.2.0 \
    torch==2.0.0 \
    optuna==3.5.0 \
    torchvision==0.15.1 -f https://download.pytorch.org/whl/cu118

# Copy your Flask app code into the Docker image
COPY flask_app /app

# Set working directory
WORKDIR /app

# Define the command to run your app using gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "9000", "app:app"]
