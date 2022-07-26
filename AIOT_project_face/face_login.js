var express = require('express');
var io = require('socket.io');
var exec = require('child_process').exec;
var app = express();
var app2 = express();

app.use(express.static("www"));
app.use(express.static("WebCam"));

var server = app.listen(5438, function() {
	console.log('伺服器在5438埠口開工了。');
});

var serverPy = app2.listen(5450, function() {
	console.log('伺服器在5450埠口開工了。等待 Python 連線。');
});

var sio = io.listen(server);
var sioPy = io.listen(serverPy);
var outerSocket;
var outerSocketPy;
var userName = '';
var userToken = 0;
var imageStream = '';

sioPy.on('connection', function(socketPy) {
    outerSocketPy = socketPy;
    console.log('connected from python');
    socketPy.on('dataPy', function(data) {
        userName = data;
        console.log('get userName from python-->' + userName);
        // socketPy.emit('NodeOK','OK userName: '+userName); // NodeOK 事件改由獲取 Token 之後再發送給 python
    });

    socketPy.on('dataPyToken', function(data) {
        userToken = data;
        console.log('get userToken from python-->' + userToken);
        socketPy.emit('NodeOK','OK userToken: '+userToken);
    });

    // 接收照片串流並發送到前端
    socketPy.on('dataPyStream',function(data) {
        // console.log('get dataStream from python');
        // console.log(data); // 監看用
        // --python 用 socketio 傳來的圖檔串流 data 是 base64 編碼的 buffer 物件(其實是陣列),
        // --要再轉換回字串, 才能傳到前端顯示出來
        // --因為從 python 傳來時已是 base64 編碼, 所以此處 toString('編碼參數') 的編碼參數不必再設定.
        // --javascript 的 Buffer toString() 支援多種編碼, 常見的有 'utf8','hex','base64' 
        imageStream = Buffer.from(data, 'base64').toString()
        // imageStream = data; // 直接用 data 是不行的, 已失敗! 上面 Buffer 轉字串才有成功!
        // 發送照片串流到前端顯示
        outerSocket.emit('liveCam', imageStream);
    });
    
});

var flgShot = false;

sio.on('connection', function(socket) {
    outerSocket = socket;
	socket.on('disconnect', function() {
		flgShot = false;
	});

	socket.on('start', function() {
        flgShot = true;
        console.log('開始拍照......');
        takePhoto(socket);
    });
    socket.on('stop', function() {
        flgShot = false;
        outerSocketPy.emit('cameraStop','stop camera')
        //開始人臉識別
        // faceLogin(socket);
    });
});


function takePhoto(socket) {
    // ---使用 Raspberry Pi 指令拍照------
    // var cmd = 'raspistill -w 640 -h 480 -o ./www/images/photo.png -t 5 -q 40';
    // ---使用 python 程式拍照, 存檔的檔名路徑 www/images/photo.png------
    var cmd = 'python3 ispan_camera.py -c haarcascades/haarcascade_frontalface_alt.xml -o www/images/';
    exec(cmd, function(error, stdout, stderr) {	
      if (error != null) {
        console.log("出錯了！" + error);
        throw error;
      } else {
        console.log("拍攝完成！");
        console.log("來自 python camera 訊息--> " + stdout);
        // 發送照片檔路徑到前端顯示
        // socket.emit('liveCam', 'photo.png?r=' + Math.floor(Math.random() * 100000));
        
        // if (flgShot) {
        //     takePhoto(socket);
        // } else {
        //     console.log('停止拍攝。');
        // }

        console.log('開始 python 人臉識別......');
        //開始人臉識別
        faceLogin(socket);
      }
    });
}

//人臉識別函數
function faceLogin(socket) {
    var cmd = 'python3 recognize_face.py -i www/images/photoCheck.png';
    // var cmd = 'python3 recognize_demoUse.py -i www/images/photo.jpg';
    exec(cmd, function(error, stdout, stderr) {
        if (error != null) {
            console.log("出錯了！" + error);
            throw error;
        } else {
            console.log("人臉識別完成！ " + userName);
            console.log("來自 python 人臉識別訊息--> ", stdout)
            socket.emit('userName', userName);
            socket.emit('userToken', userToken);
            socket.emit('afterCheck', 'afterCheck.png?r=' + Math.floor(Math.random() * 100000));

            //if (shot) {
            //   takePhoto(socket);
            //} else {
            //    console.log('停止拍攝。');
            //}
        }
    });
}