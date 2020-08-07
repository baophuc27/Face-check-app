from face_detector.detector import Detector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template, jsonify, request
import threading
import json
import cv2
import time
from fb.database import Database
from fb.storage import Storage
from datetime import datetime
import numpy as np
import requests

outputFrame = None
lock = threading.Lock()
app = Flask(__name__)
vs = VideoStream(src=0).start()
time.sleep(2.0)
detector = Detector()
hostname = "http://0.0.0.0:5000/"


# Google cloud storage to store image
storage = Storage().storage

# Firebase realtime database
database = Database().database


@app.route("/")
def index():
    # return jsonify({"index": True})
    return render_template("index.html")



def detect_face(frame):
    global vs, outputFrame
    outputFrame = detector.processs(frame)
    return outputFrame


def gen_image():
    global vs, outputFrame, frame
    while True:
        frame = vs.read()
        frame = cv2.flip(frame, 1)
        outputFrame = detect_face(frame)
        if outputFrame is not None:
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

        if not flag:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + bytearray(encodedImage) + b"\r\n"
        )


def gen_check():
    global vs, outputFrame, frame
    frame = vs.read()
    flag = detector.reg_face(frame)
    

@app.route("/webcam")
def webcam():
    return Response(gen_image(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/check")
def check():
    gen_check()
    return render_template("index.html")


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


@app.route("/getdata")
def get_data():
    link = upload_image(frame)
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
    embedding = np.asarray(detector.reg_face(frame))
    print(type(embedding))
    print(embedding.shape)
    embedding = str(embedding)
    return jsonify(time=timestamp, link=link, embedding=embedding)


@app.route("/test")
def test():
    return jsonify({"success": True})


@app.route("/detect", methods=["POST"])
def detect():
    r = requests.get(hostname + "getdata")
    data = r.json()
    database.child("user").push(data)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
vs.stop()