FROM python:3.8-slim
COPY . /app
WORKDIR /app
RUN apt-get update
RUN apt-get install -y poppler-utils
RUN apt-get install -y ffmpeg libsm6 libxext6
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["-u", "app.py"]
