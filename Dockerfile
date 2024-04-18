FROM python:3.11
ENV PYTHONUNBUFFERED 1

# Update apt packages
RUN apt update &&  \
    apt upgrade -y && \
    apt install curl build-essential -y

# Install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

RUN mkdir /code
WORKDIR /code

ADD . /code/

RUN poetry install
