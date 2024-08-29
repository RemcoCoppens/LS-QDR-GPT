@echo off

REM Set the HOME environment variable
set HOME=C:\path\to\label-studio-data

REM Activate the conda environment
call C:\path\to\conda\Scripts\activate.bat QDR-env

REM Start Label Studio
start label-studio start --port 8080

REM Start the Flask app
python app.py
