FROM mcr.microsoft.com/azure-functions/python:4

WORKDIR /app
RUN apt update && apt upgrade -y && apt install -y mariadb-client libmariadb-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /


