# pull official base image
FROM python:3.12-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements_docker.txt .
RUN pip install -r requirements_docker.txt
RUN pip install "psycopg[binary]" 

# copy project
COPY . .
