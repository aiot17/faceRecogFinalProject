# to create a camera image stream and send to nodejs
from imutils.video import VideoStream
# import argparse
import imutils
import time
import cv2
# import os
# import sys
import socketio
import base64

# from sqlalchemy import false # 沒用到

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

# open camera and read a image
# use USB camera
# vs = VideoStream(src=0).start()
# use Rpi camera
vs = VideoStream(usePiCamera=True).start()
time.sleep(1) #time.sleep(2.0)

flgStart = True
iCount = 1
# loop over the frames from the video stream
while flgStart:
    frame = vs.read()
    orig = frame.copy()
    frame = imutils.resize(frame, width=640)

    # draw a rectangle in the image
    cv2.rectangle(frame, (193, 60), (446, 340), (0, 140, 255), 4)
    # cv2.imshow("Frame", frame)
    retval, buffer = cv2.imencode('.jpg',frame)
    jpg_as_text = base64.b64encode(buffer) # 轉換為 base64 編碼
    # jpg_as_text = buffer # 測試不轉換為 base64 編碼
    # print(jpg_as_text)
    # print("---check data stream---")
    sio.emit("dataStream",jpg_as_text) # send data stream to nodejs
    print("已拍攝: " , iCount, end="                    \r") # 顯示已拍攝次數(並一直覆蓋同一行)
    iCount += 1
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    # flgStar = false

print()
print("[INFO] cleaning up...")
# cmd = input("please input......")
sio.disconnect()
cv2.destroyAllWindows()
vs.stop()