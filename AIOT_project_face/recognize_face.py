# USAGE
# python recognize.py --detector face_detection_model \
#    --embedding-model openface_nn4.small2.v1.t7 \
#    --recognizer output/recognizer.pickle \
#    --le output/le.pickle --image images/adrian.jpg

# import the necessary packages
import numpy as np
import argparse
import imutils
import pickle
import cv2
import os
import socket
import socketio
import requests
import time

startTime = time.time()
# user name and token to pass to nodejs
userName = ''
userToken = 0

# below function send userName to JavaWeb through socket
def yes(name):
    # msg = {"azen":"1","Chao":"2","Dav":"3","hubert_test":"4","kk":"5","TzuYao":"6"}.get(name)
    # ------使用 socket 傳輸的方法----------------------------------
    # msg = name + "\n"
    # HOST = '192.168.22.203'
    # PORT = 4200
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((HOST, PORT))
    # s.send(msg.encode())
    # s.close()
    # # print(msg)
    # # mainSocket(HOST,PORT,msg)
    # ------使用 HTTP 傳輸的方法-------------------------------------
    HOST = '192.168.22.98'
    PORT = 8080
    url = f"http://{HOST}:{PORT}/Demo/pi?user={name}"
    try:
        r = requests.get(url,timeout=3)
        print("from JavaWeb--> ",r.text,",text length=", len(r.text))
        if len(r.text) == 20:
            return r.text
        else:
            return  0
    except:
        print("JavaWeb timeout!")
        return 0
    # print("from JavaWeb--> ",r.text)

# use socketio to link to nodejs
sio = socketio.Client()

@sio.event
def connect():
    print('connection established')
    # sio.emit('dataPy', "0") # for demo test

@sio.event
def disconnect():
    print('disconnected from server')
    sio.disconnect()

@sio.on('NodeOK')  # get a 'NodeOK' event
def catch_data(data):
    print('data from node= ', data)
    sio.disconnect()

sio.connect('http://localhost:5450')
# sio.emit('dataPy', "abc") # for demo test

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False,default='./images/adrian.jpg',
    help="path to input image")
ap.add_argument("-d", "--detector", required=False,default='face_detection_model',
    help="path to OpenCV's deep learning face detector")
ap.add_argument("-m", "--embedding-model", required=False,default='openface_nn4.small2.v1.t7',
    help="path to OpenCV's deep learning face embedding model")
ap.add_argument("-r", "--recognizer", required=False,default='output/recognizer.pickle',
    help="path to model trained to recognize faces")
ap.add_argument("-l", "--le", required=False,default='output/le.pickle',
    help="path to label encoder")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
    help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# load our serialized face detector from disk
print("[INFO] loading face detector...")
protoPath = os.path.sep.join([args["detector"], "deploy.prototxt"])
modelPath = os.path.sep.join([args["detector"],
    "res10_300x300_ssd_iter_140000_fp16.caffemodel"])
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

# load our serialized face embedding model from disk
print("[INFO] loading face recognizer...")
embedder = cv2.dnn.readNetFromTorch(args["embedding_model"])

# load the actual face recognition model along with the label encoder
recognizer = pickle.loads(open(args["recognizer"], "rb").read())
le = pickle.loads(open(args["le"], "rb").read())

# load the image, resize it to have a width of 600 pixels (while
# maintaining the aspect ratio), and then grab the image dimensions
image = cv2.imread(args["image"])
image = imutils.resize(image, width=640)
(h, w) = image.shape[:2]

# construct a blob from the image
imageBlob = cv2.dnn.blobFromImage(
    cv2.resize(image, (300, 300)), 1.0, (300, 300),
    (104.0, 177.0, 123.0), swapRB=False, crop=False)

# apply OpenCV's deep learning-based face detector to localize
# faces in the input image
detector.setInput(imageBlob)
detections = detector.forward()

# loop over the detections(如果只偵測到一張人臉, 則只會執行一次)
for i in range(0, detections.shape[2]):
    # extract the confidence (i.e., probability) associated with the
    # prediction
    confidence = detections[0, 0, i, 2]

    # filter out weak detections
    if confidence > args["confidence"]:
        # compute the (x, y)-coordinates of the bounding box for the
        # face
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        # extract the face ROI
        face = image[startY:endY, startX:endX]
        (fH, fW) = face.shape[:2]

        # ensure the face width and height are sufficiently large
        if fW < 20 or fH < 20:
            continue

        # construct a blob for the face ROI, then pass the blob
        # through our face embedding model to obtain the 128-d
        # quantification of the face
        faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96),
            (0, 0, 0), swapRB=True, crop=False)
        embedder.setInput(faceBlob)
        vec = embedder.forward()

        # perform classification to recognize the face
        preds = recognizer.predict_proba(vec)[0]
        j = np.argmax(preds)
        proba = preds[j]
        name = le.classes_[j]
        # print the name for Azen check
        print('name({0})= {1},{2:.2f}%'.format(i,name,proba*100))
        if proba > 0.5:
            userName = name
        else:
            userName = 'unknown'

        # draw the bounding box of the face along with the associated
        # probability
        # text = "{}: {:.2f}%".format(name, proba * 100)
        # text = "{}: {:.2f}%".format(userName, proba * 100) # change to use userName to force unknown if proba < 50%
        text = "{}".format(userName) # 正式版不輸出機率%
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(image, (startX, startY), (endX, endY),
            (0, 0, 255), 2)
        cv2.putText(image, text, (startX, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

# 觀察 usrName
# print("識別完成,userName=", userName)
if userName == "":
    print("python 識別不到人臉!")
    userName = 'unknown'
# save the output image
cv2.imwrite("www/images/afterCheck.png",image)
# show the output image
#cv2.imshow("Image", image)
#cv2.waitKey(0)

# pass userName to JavaWeb if face check is ok
userToken = yes(userName) if userName != 'unknown' else 0
# pass userName and userToken to nodejs through socketio
sio.emit('dataPy',userName)
sio.emit('dataPyToken',userToken)
sio.wait()
endTime = time.time()
deltaTime = endTime - startTime
print("人臉辨識歷時: %.2f s" % deltaTime)
