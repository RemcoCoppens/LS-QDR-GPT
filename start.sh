#!/bin/sh

# Activate the conda environment
. /opt/conda/etc/profile.d/conda.sh
conda activate ls-venv

#Start Label Studio in the background
label-studio start --port 8080 &

# Start the Flask app
python app.py