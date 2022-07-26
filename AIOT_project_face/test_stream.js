var express = require('express');
var io = require('socket.io');
var exec = require('child_process').exec;
var app = express();
var app2 = express();
var imageStream = "";

app.use(express.static("www"));

var server = app.listen(5438, function() {
	console.log('伺服器在5438埠口開工了。');
});

var serverPy = app2.listen(5450, function() {
    // 這個通道是 python 拍照傳送串流用的
	console.log('伺服器在5450埠口開工了。等待 Python 連線。');
});

var sio = io.listen(server);
var sioPy = io.listen(serverPy);
var userName = '';

sioPy.on('connection', function(socketPy) {
    console.log('connected from python');
    socketPy.on('dataPy', function(data) {
        userName = data;
        console.log('get data from python-->' + userName);
        socketPy.emit('NodeOK','OK '+userName);
    });
    // socketPy.emit('NodeOK','OK');
    socketPy.on('dataStream',function(data) {
        // console.log('get dataStream from python');
        // console.log(data);
        // --python 用 socketio 傳來的圖檔串流 data 是 base64 編碼的 buffer 物件(其實是陣列),
        // --要再轉換回字串, 才能傳到前端顯示出來
        // --因為從 python 傳來時已是 base64 編碼, 所以此處 toString('編碼參數') 的編碼參數不必再設定.
        // --javascript 的 Buffer toString() 支援多種編碼, 常見的有 'utf8','hex','base64' 
        imageStream = Buffer.from(data, 'base64').toString()
        // imageStream = data; // 直接用 data 是不行的, 已失敗! 上面 Buffer 轉字串才有成功!

    });
});

sio.on('connection', function(socket) {
	socket.on('disconnect', function() {
		shot = false;
	});

	socket.on('start', function() {
        shot = true;

        // takePhoto(socket);
        setInterval(() => {
            sendStream(socket);
        },50);
        
    });
    socket.on('stop', function() {
        shot = false;
        //開始人臉識別
        // faceLogin(socket);
    });
});

function sendStream(socket) {
    socket.emit('liveCam', imageStream);
}

function takePhoto(socket) {
    // 使用 Raspberry Pi 指令拍照
    // var cmd = 'raspistill -w 640 -h 480 -o ./www/images/photo.png -t 5 -q 40';
    // 使用上課程式拍照, 檔名路徑 www/images/photo.png
    var cmd = 'python3 ispan_camera.py -c haarcascades/haarcascade_frontalface_alt.xml -o www/images/';
    exec(cmd, function(error, stdout, stderr) {	
      if (error != null) {
        console.log("出錯了！" + error);
        throw error;
      } else {
        console.log("拍攝完成！");
        socket.emit('liveCam', 'photo.png?r=' + Math.floor(Math.random() * 100000));
        
        if (shot) {
            takePhoto(socket);
        } else {
            console.log('停止拍攝。');
        }
      }
    });
}
