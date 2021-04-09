## Description
This is the python flask application, which takes pdf file with text layer as
an input and produces an archive with images. On each image every line is within bbox.
All bbox coordinates are taken from text layer, so if the user wants to have great result he should download pdf with "good" text layer.
This application accepts files only with the pdf extension.

#### Instructions

First of all, you need to have installed [Docker](https://docs.docker.com/get-docker/)

#### Clone this repository to some directory and move into it:

```bash
git clone git@github.com:ezhopets/flask-bbox.git path_you_want
cd path_you_want
```

#### Build application:

```bash
docker build -t flask_bbox:latest .
```

#### Run the container:

```bash
docker run -p 8080:5000 flask_bbox:latest
```

Then open http://localhost:8080 in your browser to check.
Also you can check it with your host ip and port 8080 from another device with
the same network (for example: http://192.168.1.104:8080).
