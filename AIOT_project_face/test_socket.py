import socket

# 尾端須加上 '\n', 也就是 EOL(end of line), Java socket server 才會回傳訊息.
# 這是因為 Java 用 readLine() 函數讀入訊息, 需要有 EOL 來判斷一行是否結束
msg = 'abc88' + '\n'
# HOST = '192.168.22.77'
HOST = '127.0.0.1'
PORT = 30000
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((HOST, PORT))
# # socket.sendall() 與 socket.send() 的差別是 sendall() 會調用 send(),
# # 直到把所有 buffer 內的數據傳送完或者有錯誤產生.
# s.sendall(msg.encode())
# # 1024 是接收的 buffer 大小
# data = s.recv(1024).decode()
# print('receive-->', data)
# s.close()

while True:
    msg = input("Please input msg: ")
    if msg == 'q':
        break
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    # 尾端須加上 '\n', 也就是 EOL(end of line), Java socket server 才會回傳訊息.
    # 這是因為 Java 用 readLine() 函數讀入訊息, 需要有 EOL 來判斷一行是否結束
    msg = msg + '\n' 
    # socket.sendall() 與 socket.send() 的差別是 sendall() 會調用 send(),
    # 直到把所有 buffer 內的數據傳送完或者有錯誤產生.
    s.sendall(msg.encode())
    # 1024 是接收的 buffer 大小
    data = s.recv(1024).decode()
    print("server send : {}".format(data))
    print("length of data= ",len(data))
    # 對 python 來說, 從 Java socket server 傳來的字串尾帶有 '\r\n'
    if (data == "server send======\r\n"):
        print("has \\r\\n")
    else:
        print("can't get \\r\\n")
    print()
    s.close()
print('--end--')