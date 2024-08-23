#!/bin/sh

# Set the HOME environment variable to ensure Label Studio stores data in the correct directory
export HOME=/app/label-studio-data

# Activate the conda environment
. /opt/conda/etc/profile.d/conda.sh
conda activate QDR-env

#Start Label Studio in the background
label-studio start --port 8080 &

# Start the Flask app
python app.py
