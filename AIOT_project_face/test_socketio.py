# import socket
import socketio

# msg = "data"
# print(f"this is {msg}")
# HOST = '127.0.0.1'
# PORT = 5450
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((HOST, PORT))
# s.send(msg.encode())
# print('send-->',msg)
# s.close()

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')
    # sio.emit('dataPy', "0")

@sio.event
def disconnect():
    print('disconnected from server')
    sio.disconnect()

@sio.on('NodeOK')
def catch_data(data):
    print('data= ', data)
    sio.disconnect()

sio.connect('http://localhost:5450')
sio.emit('dataPy', "abc")

sio.wait()
#sio.disconnect()
