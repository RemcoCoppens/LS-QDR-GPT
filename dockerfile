# Use the official Miniconda image as the base image (smaller and more efficient than Anaconda)
FROM continuumio/miniconda3

# Set the working directory in the container
WORKDIR /app

# Copy the environment.yml file to the container
COPY environment.yml .

# Create the conda environment based on environment.yml
RUN conda env create -f environment.yml --quiet && conda clean -afy

# Activate the conda environment, install label-studio, and ensure subsequent RUN commands use the environment
SHELL ["conda", "run", "-n", "QDR-env", "/bin/bash", "-c"]

# Install label-studio within the conda environment
RUN pip install label-studio

# Set the environment variable for Label Studio's data directory
ENV LABEL_STUDIO_ROOT /app/label-studio-data

# Copy your start.sh script explicitly to the working directory
COPY start.sh /app/start.sh

# Copy all your application files to the working directory
COPY . /app

# Ensure the start.sh script is executable
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 5000 8080

# Start the Flask app using the conda environment
CMD ["conda", "run", "--no-capture-output", "-n", "QDR-env", "./start.sh"]
