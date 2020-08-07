from imutils.video import VideoStream
from flask import render_template, jsonify, request, Flask , Response
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

outputFrame = None
app = Flask(__name__)
vs = VideoStream(src=0).start()
time.sleep(2.0)
# detector = Detector()
hostname = "http://0.0.0.0:5000/"
FACE_DETECTOR_SERVER = "http://face-detector.azurewebsites.net/detect?img_url="

# Google cloud storage to store image
storage = Storage().storage

# Firebase realtime database
database = Database().database


@app.route("/")
def index():
    return render_template("index.html")



def detect_face(frame):
    global vs, outputFrame
    outputFrame = detector.processs(frame)
    return outputFrame


def gen_image():
    global vs, frame
    while True:
        frame = vs.read()
        frame = cv2.flip(frame, 1)
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


@app.route("/download", methods=["POST"])
def download():
    storage.child("user1/image").download("image.jpg")
    return render_template("index.html")

@app.route("/getfb")
def getfb():
    res= database.child('user').get()
    users=[]
    embeddings=[]
    for user in res.each():
        val=user.val()
        embedding = val['embedding']
        embedding=np.fromstring(embedding[1:-1],dtype='float',sep=' ').reshape(512,1)
        users.append({"link":val["link"],"time":val["time"]})
        embeddings.append(embedding)

    indexes=get_similar_index(embeddings,embedding)
    data = [users[index[0]] for index in indexes]
    json_data = json.dumps(data)
    json_data = json.loads(json_data)
    return render_template("index.html",data = data)

def face_distance(face_encodings, face_to_compare):
    face_dist_value = np.linalg.norm(face_encodings - face_to_compare, axis=1)
    return face_dist_value

def get_similar_index(face_encodings,face_to_compare):
    if len(face_encodings) == 0:
        return np.empty((0))
    indexes = np.argwhere(face_distance(face_encodings,face_to_compare) < configs.THRESHOLD )
    return indexes

@app.route("/getdata")
def get_data():
    link = upload_image(frame)
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
    embedding = get_embedding(link)
    embedding =str(embedding)
    return jsonify(time=timestamp, link=link, embedding =embedding)

def get_embedding(url):
    """
    Encrypt the url and send to azure server
    """
    image_handler = Handler(url)
    url=image_handler.get_url()
    res=requests.post(FACE_DETECTOR_SERVER+str(url))
    data=res.json()
    emb=data["embedding"]
    embedding=np.fromstring(emb[1:-1],dtype=float,sep=' ')
    return embedding.reshape((1,512))


@app.route("/detect", methods=["POST"])
def detect():
    r = requests.get(hostname + "getdata")
    data = r.json()
    database.child("user").push(data)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")

vs.stop()