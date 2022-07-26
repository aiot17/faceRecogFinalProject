// Node.js 後端
// 接收前端傳來的影像串流, 並透過 Socket.io 傳給 Python 顯示
// Import builtin NodeJS modules to instantiate the service
const https = require("https");
const fs = require("fs");
var io = require('socket.io');

// Import the express module
const express = require("express");

// Instantiate an Express application
const app = express();
var app2 = express(); // for python connection
app.use(express.static("www"));

// Create a NodeJS HTTPS listener on port 4000 that points to the Express app
// Use a callback function to tell when the server is created.
// https
//   .createServer(app)
//   .listen(4000, ()=>{
//     console.log('server is runing at port 4000')
//   });

var server = https
  .createServer(
		// Provide the private and public key to the server by reading each
		// file's content with the readFileSync() method.
    {
      key: fs.readFileSync("key.pem"),
      cert: fs.readFileSync("cert.pem"),
    },
    app
  )
  .listen(4000, () => {
    console.log("serever is runing at port 4000. 等待前端連線......");
  });

// Create an try point route for the Express app listening on port 4000.
// This code tells the service to listed to any request coming to the / route.
// Once the request is received, it will display a message "Hello from express server."
app.get('/', (req,res) => {
    res.send("Hello from express server.")
    // console.log("Send WebCam.html");
    // res.sendFile(__dirname + "/WebCam.html");
});

// create server for pythone connection(--使用 https 網站的方法失敗, 無法讓 python 連線!--)
// var serverPy = https
//   .createServer(
// 		// Provide the private and public key to the server by reading each
// 		// file's content with the readFileSync() method.
//     {
//       key: fs.readFileSync("key.pem"),
//       cert: fs.readFileSync("cert.pem"),
//     },
//     app2
//   )
//   .listen(4050, () => {
//     console.log("serever is runing at port 4050. 等待 python 連線......");
//   });

// 以下使用 http 網站給 python 連線的方式成功
var serverPy = app2.listen(4050, function() {
	console.log('伺服器在4050埠口開工了。等待 Python 連線。');
});

var sioPy = io.listen(serverPy);
var sio = io.listen(server);
var outerSocketPy;
var outerSocket;
var flgPyReady = false;  // 表示 python 是否已準備好接收串流
var flgSioReady = false; // 表示前端 socket 是否連線

//與 python socket.io 通訊的事件處理
sioPy.on('connection', function(socketPy) {
    outerSocketPy = socketPy;
    console.log('python 建立連線......');
    flgPyReady = true;

	socketPy.on('disconnect', function() {
		console.log("python 中斷連線!");
    flgPyReady = false;
	});

  socketPy.on('pyReady', function() {
    // pyReady 事件代表 python 等待傳送中
    flgPyReady = true;
    // 通知前端 python 等待傳送中
    if (flgSioReady) {
      outerSocket.emit("pyReady"); 
		  // console.log("接收python 訊號後, 已傳送 pyReady 事件給前端");
    }
    
	});

});

// 與前端 socket.io 通訊的事件處理
// var flgShot = false;
sio.on('connection', function(socket) {
  console.log('前端 socketio 建立連線');
  flgSioReady = true;
  outerSocket = socket;
  // console.log('flgPyReady= ' + flgPyReady); // 監看用
  if (flgPyReady) {
    socket.emit("pyReady");
    // console.log("初始連線 已傳送 pyReady 事件給 前端");
  }

	socket.on('disconnect', function() {
        // flgShot = false;
    flgSioReady = false;
		console.log("前端 socketio 中斷連線!");
	});

	socket.on('sendPhoto', function(data) {
        // flgShot = true;
        // console.log('前端傳來照片......');
        // console.log(data.slice(0,50) + '......');
        // 圖片串流字串轉 Buffer
        imgBuffer = Buffer.from(data,'base64');
        // 發送圖片 Buffer 串流給 python
        if (flgPyReady) {
          outerSocketPy.emit('sendPhotoPy',imgBuffer);
          flgPyReady = false;
        }
    });

    socket.on('stop', function() {
        // flgShot = false;
        console.log("前端傳來停止拍照!");
    });
});
