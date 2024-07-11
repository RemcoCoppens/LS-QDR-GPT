# Use the official CUDA 12.4.1 image as the base image
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

# Install dependencies and Miniconda
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    && rm -rf /var/lib/apt/lists/*

# Download and install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda \
    && rm Miniconda3-latest-Linux-x86_64.sh

# Set up the path environment variable for conda
ENV PATH=/opt/conda/bin:$PATH

# Initialize conda for bash shell
RUN conda init bash

# Set CONDA_OVERRIDE_CUDA to force a specific CUDA version
ENV CONDA_OVERRIDE_CUDA=12.4

# Copy the environment.yml file to the container
COPY environment.yml .

# Create the conda environment
RUN conda env create -f environment.yml

# Ensure the environment is activated
SHELL ["conda", "run", "-n", "ls-venv", "/bin/bash", "-c"]

# Install label-studio within the conda environment
RUN conda run -n ls-venv pip install label-studio

# Copy your application files
COPY . /app
WORKDIR /app

# Expose ports
EXPOSE 5000 8080

# Ensure the start.sh script is executable
RUN chmod +x start.sh

# Activate environment and start the Flask app
# CMD ["conda", "run", "--no-capture-output", "-n", "ls-venv", "sh", "./start.sh"]
CMD ["conda", "run", "--no-capture-output", "-n", "ls-venv", "./start.sh"]
