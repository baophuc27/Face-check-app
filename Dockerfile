FROM python:3.6
WORKDIR /face_check
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get -y install cmake
RUN pip install -r ./requirements.txt
COPY . .
CMD "python" "app.py"

