FROM python:3.9-slim
RUN apt-get update
RUN apt-get install --no-install-recommends --assume-yes wine
RUN dpkg --add-architecture i386
RUN apt-get update
RUN apt-get install --no-install-recommends --assume-yes wine32

ENV HOST "0.0.0.0"
ENV PORT "8080"

# Create directory
RUN mkdir -p /home/app/DjuliAPIpython
WORKDIR /home/app/DjuliAPIpython

# Install libraries
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./src ./src

# Run unit tests
COPY ./test ./test
RUN pytest

CMD python3 src/main.py
