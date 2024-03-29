from imutils.video import VideoStream
from flask import render_template, jsonify, request, Flask, Response
import threading
import json
import cv2
import time
from fb.database import Database
from fb.storage import Storage
from datetime import datetime
import numpy as np
import requests
from image_handler.handler import Handler
from configs import configs
import os

outputFrame = None
app = Flask(__name__)
vs = VideoStream(src=0).start()
time.sleep(2.0)
# detector = Detector()
hostname = "http://0.0.0.0:5000/"
FACE_DETECTOR_SERVER = "http://0.0.0.0:8002/detect?img_url="

# Google cloud storage to store image
storage = Storage().storage

# Firebase realtime database
database = Database().database


@app.route("/")
def index():
    return render_template("index.html")


def gen_image():
    global vs, frame
    while True:
        frame = vs.read()
        # frame = cv2.flip(frame, 1)
        if frame is not None:
            (flag, encodedImage) = cv2.imencode(".jpg", frame)

        if not flag:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + bytearray(encodedImage) + b"\r\n"
        )


@app.route("/webcam")
def webcam():
    return Response(gen_image(), mimetype="multipart/x-mixed-replace; boundary=frame")


def upload_image(frame):

    path = "user1/" + str(int(time.time()))
    (_, encodedImage) = cv2.imencode(".jpg", frame)
    storage.child(path).put(bytearray(encodedImage))
    link = storage.child(path).get_url(None)
    return link


# @app.route("/download", methods=["POST"])
# def download():
#     storage.child("user1/image").download("image.jpg")
#     return render_template("index.html")

def face_distance(face_encodings, face_to_compare):
    face_dist_value = []
    # for encoding in face_encodings:
    #     # face_dist_value.append(
    #     #     np.dot(encoding, face_to_compare)
    #     #     / ((np.linalg.norm(encoding) * np.linalg.norm(face_to_compare)))
    #     # )
    face_dist_value=np.linalg.norm(face_encodings-face_to_compare,axis=1)
    print(face_dist_value)
    return np.asarray(face_dist_value)


def get_similar_index(face_encodings, face_to_compare):
    if len(face_encodings) == 0:
        return np.empty((0))
    indexes = np.argwhere(
        face_distance(face_encodings, face_to_compare) < configs.EUCLID_THRESHOLD
    )
    return indexes

@app.route("/detect", methods=["POST"])
def detect():
    start_time = time.time()
    similar_data=[]
    index = []
    #Save frames in local
    capture_faces()

    index = compare_face()
    url = hostname + "getdata"
    # if len(index) == 0:
    r = requests.get(url)
    data = r.json()
    database.child("user").push(data)
    similar_data = get_similar_data(index)
    print("--- %s seconds ---" % (time.time() - start_time))
    return render_template("index.html", data=similar_data)


def compare_face():
    similar_index = []
    embeddings = []
    url = hostname + "getdata"
    for i in range(configs.VOTE):
        params= {"filename":str(i)}
        r = requests.get(url,params=params)
        data = r.json()
        embeddings.append(data["embedding"])
    similar_index = compare_data(embeddings)
    unique_index, counts = np.unique(similar_index, return_counts=True)
    print(unique_index)
    print(counts)
    index = unique_index[counts >= configs.VOTE_THRESHOLD]
    return index


def capture_faces():
    basepath="./faces"
    for i in range(configs.VOTE):
        name = os.path.join(basepath,str(i))+".jpg"
        cv2.imwrite(name,frame[::2,::2])
        time.sleep(configs.TIME_PER_VOTE)

@app.route("/getdata",methods=['GET'])
def get_data():
    filename=request.args.get('filename')
    if not filename:
        filename = '0.jpg'
    else:
        filename = filename +".jpg"
    image_path=os.path.join('./faces',filename)
    # image_path = './Images/rooney5.jpg'
    image = cv2.imread(image_path)
    link = upload_image(image)
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
    embedding = get_embedding(link)
    embedding = str(embedding)
    return jsonify(time=timestamp, link=link, embedding=embedding)


def get_embedding(url):
    """
    Encrypt the url and send to azure server
    """
    image_handler = Handler(url)
    url = image_handler.get_url()
    res = requests.post(FACE_DETECTOR_SERVER + str(url))
    data = res.json()
    emb = data["embedding"]
    embedding = np.fromstring(emb[1:-1], dtype=float, sep=" ")
    return embedding.reshape(512)


def compare_data(embedding_compares):
    res = database.child("user").get()
    users = []
    embeddings = []
    for user in res.each():
        val = user.val()
        embedding = val["embedding"]
        embedding = np.fromstring(embedding[1:-1], dtype="float", sep=" ").reshape(512)
        users.append({"link": val["link"], "time": val["time"]})
        embeddings.append(embedding)
    embeddings = np.asarray(embeddings)
    indexes = []
    for embedding_compare in embedding_compares:
        embedding_compare = np.fromstring(
            embedding_compare[1:-1], dtype="float", sep=" "
        ).reshape(512)
        index = get_similar_index(embeddings, embedding_compare)
        indexes.extend(index)
    data = [index[0] for index in indexes]
    return data


def get_similar_data(indexes):
    res = database.child("user").get()
    users = []
    embeddings = []
    for user in res.each():
        val = user.val()
        embedding = val["embedding"]
        embedding = np.fromstring(embedding[1:-1], dtype="float", sep=" ").reshape(512)
        users.append({"link": val["link"], "time": val["time"]})
        embeddings.append(embedding)
    data = [users[i] for i in indexes]
    return data


if __name__ == "__main__":
    app.run(host="0.0.0.0")

vs.stop()
