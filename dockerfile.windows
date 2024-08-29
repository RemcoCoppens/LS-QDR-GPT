# Use a Miniconda base image that is compatible with Windows
FROM mcr.microsoft.com/windows/servercore:ltsc2019

WORKDIR /app

COPY environment.yml .

RUN conda env create -f environment.yml --quiet && conda clean -afy

COPY . /app

# Set the environment variable for Label Studio's data directory
ENV LABEL_STUDIO_ROOT C:\app\label-studio-data

EXPOSE 5000 8080

CMD ["cmd.exe", "/c", "start.bat"]
