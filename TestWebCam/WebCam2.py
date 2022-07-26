# 接收 Node.js 後端網站透過 socketio 傳來的影像串流並顯示
# import the necessary packages
from imutils.video import VideoStream
# import argparse
import imutils
import time
import cv2
# import os
# import sys
import socketio
# import base64
import numpy as np

dataBuffer = '' # 用來接收圖片串流
flgUpdate = False # 用來控制是否更新圖片內容
flgHasImg = False # 標示是否有圖
flgDisconnect = False # 標示是否已和 Node.js 斷線
intCount = 0 # 計算 fps 用

# use socketio to link to nodejs, 建立 socketio 連線
sio = socketio.Client()

@sio.event
def connect():
    print('python to Node.js connection established')
    sio.emit('pyReady') # 通知 Node.js 可以傳送圖片串流

@sio.event
def disconnect():
    global flgDisconnect
    print('python disconnected from Node.js server')
    sio.disconnect()
    flgDisconnect = True

# 接收 sendPhotoPy 事件, 也就是 Node.js 傳來圖片串流 Buffer
@sio.on('sendPhotoPy')  # get a 'sendPhotoPy' event
def catch_data(data):
    # print('data Buffer from node= ', data[0:60])
    # print('type of img data Buffer:', type(data)) # <class 'bytes'>
    global dataBuffer
    global flgUpdate
    dataBuffer = data # 用 dataBuffer 變數接收串流資料
    flgUpdate = True
 
sio.connect('http://localhost:4050')
# sio.emit('dataPy', "abc") # for demo test

def showImg():
    # print("show img")
    global dataBuffer
    global flgUpdate
    global flgHasImg
    global flgDisconnect
    global intCount
    imgFrame = ''
    while True:
        if flgUpdate == True:
            if (intCount == 0):
                startTime = time.time() # 開始傳入照片的時間
            intCount += 1
            # print("dataBuffer: ",dataBuffer[0:15],"......",dataBuffer[-15:],end='\r') # 監看用
            # 存檔之後, 發現是一個標準 png 檔, size 320x240
            # with open(r'c:/temp/temp.png', 'wb') as f:
            #     f.write(dataBuffer)
            # base64 解碼
            # imgData = base64.b64decode(dataBuffer) # 不行!! 不需要 base64解碼.
            # ---最後發現, 不用 base64 解碼可以成功------------
            # imgData = dataBuffer
            # print("imgData: ", imgData[:20],"......",imgData[-20:])
            # imgFrame = cv2.imdecode(imgData,cv2.IMREAD_COLOR) # 這行不行,需要轉 numpy array 才可以!!
            imgFrame = cv2.imdecode(np.frombuffer(dataBuffer, np.uint8),cv2.IMREAD_COLOR)
            flgHasImg = True
            # imgFrame = imutils.resize(imgFrame, width=640) # 放大成 size 640x480
            endTime = time.time()
            print("已拍攝: " , intCount, end=" 次                    \r") # 顯示已拍攝次數(並一直覆蓋同一行)

        # 有圖才能 show
        if flgHasImg == True: 
            cv2.imshow('Frame',imgFrame)

        # 圖片更新完成,接下來變更狀態為等待傳送
        if flgUpdate == True: 
            flgUpdate = False
            sio.emit('pyReady') # 通知 Node.js 可以傳送下一張

        key = cv2.waitKey(20) & 0xFF
        # if the `q` key was pressed or disconnected with Node.js, break from the loop
        if (key == ord("q")) or (flgDisconnect == True):
            sio.disconnect()
            deltaTime = endTime - startTime # 拍照時間秒數
            fps = intCount/deltaTime
            print() # 上一行是拍攝次數, 需要換行
            print("歷時: %.2f s" % deltaTime, ", 拍照速度: %.2f fps" % fps)
            break

showImg()
sio.wait()
cv2.destroyAllWindows()
