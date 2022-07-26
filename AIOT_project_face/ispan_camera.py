# USAGE
# python3 build_face_dataset.py 
#         --cascade /usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml 
#         --output dataset/yourname
#         --start 0

# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os
import sys
import socketio
import base64
import time

# from sqlalchemy import false, true # 沒用到

flgStart = True # 是否繼續拍照
# use socketio to link to nodejs, 建立 socketio 連線
sio = socketio.Client()

@sio.event
def connect():
    print('Py camera connection established')
    # sio.emit('dataPy', "0") # for demo test

@sio.event
def disconnect():
    print('Py camera disconnected from server')
    sio.disconnect()

# 接收 cameraStop 事件
@sio.on('cameraStop')  # get a 'cameraStop' event
def catch_data(data):
    global flgStart
    print('data from node= ', data)
    flgStart = False # 不再繼續拍照
    # sio.disconnect()

sio.connect('http://localhost:5450')
# sio.emit('dataPy', "abc") # for demo test

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
    help = "path to where the face cascade resides")
ap.add_argument("-o", "--output", required=True,
    help="path to output directory")
ap.add_argument("-s", "--start", type=int, default=0,
    help="start number, default is 0")
args = vars(ap.parse_args())

# check if output directory is exist
if not os.path.isdir(args['output']):
    print(f'Output directory {args["output"]} does not exist, create first...')
    sys.exit(2)

# load OpenCV's Haar cascade for face detection from disk, 載入人臉 model, 用來偵測有無人臉
detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream, allow the camera sensor to warm up,
# and initialize the total number of example faces written to disk
# thus far
print("[INFO] starting video stream...")
#vs = VideoStream(src=0).start() # 外接 usb camera
vs = VideoStream(usePiCamera=True).start() # 樹莓派提供的 camera
time.sleep(1) #time.sleep(2.0)

idx = args['start']
total = 0
iCount = 1 # 紀錄拍照次數用

startTime = time.time() # 開始拍照時間
# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream, clone it, (just
    # in case we want to write it to disk), and then resize the frame
    # so we can apply face detection faster
    frame = vs.read()
    orig = frame.copy()
    frame = imutils.resize(frame, width=640)
    # orig = frame.copy()

    # put a rectangle to limit the face size
    cv2.rectangle(frame, (193, 60), (446, 340), (0, 140, 255), 4)

    # detect faces in the grayscale frame, 偵測有無人臉
    rects = detector.detectMultiScale(
        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
        minNeighbors=5, minSize=(30, 30))

    # loop over the face detections and draw them on the frame, 將人臉框列出來
    for (x, y, w, h) in rects:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # show the output frame
    # cv2.imshow("Frame", frame)

    # 將圖片放入 buffer, 並進行 base64 編碼
    retval, buffer = cv2.imencode('.jpg',frame)
    jpg_as_text = base64.b64encode(buffer) # 轉換為 base64 編碼
     # send data stream to nodejs
    sio.emit("dataPyStream",jpg_as_text)
    print("已拍攝: " , iCount, end=" 次                    \r") # 顯示已拍攝次數(並一直覆蓋同一行)

    if flgStart == False:
        endTime = time.time() # 結束拍照時間
        # save the picture
        # ---儲存原照片, 人臉識別用
        p = os.path.sep.join([args["output"], "photoCheck.png"]) 
        cv2.imwrite(p, orig)
        # ---儲存放大照, 前端顯示用
        p = os.path.sep.join([args["output"], "photo.png"])
        cv2.imwrite(p, frame)
        print() # 換行, 才能顯示上面的已拍攝次數
        deltaTime = endTime - startTime # 拍照時間秒數
        fps = iCount/deltaTime
        print("歷時: %.2f s" % deltaTime, ", 拍照速度: %.2f fps" % fps)
        print('picture saved...')
        break
    #拍照次數 +1
    iCount += 1
    # 暫停 0.05 sec
    # time.sleep(0.05) 

    # key = cv2.waitKey(1) & 0xFF
 
    # if the `p` key was pressed, write the *original* frame to disk
    # so we can later process it and use it for face recognition
    # if key == ord("p"):
    #     p = os.path.sep.join([args["output"], "{}.png".format(
    #         str(idx).zfill(5))])
    #     cv2.imwrite(p, orig)
    #     idx += 1
    #     total += 1
    #     print(f'{total} pictures saved...')
    # if the `q` key was pressed, break from the loop
    # elif key == ord("q"):
    #     break
    # flgStart = False

# do a bit of cleanup
# print("[INFO] {} face images stored".format(total))
print("[INFO] cleaning up...")
sio.disconnect()
cv2.destroyAllWindows()
vs.stop()


