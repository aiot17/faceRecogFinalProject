var express = require('express');
var io = require('socket.io');
var exec = require('child_process').exec;
var app = express();

app.use(express.static("www"));

var server = app.listen(5438, function() {
	console.log('伺服器在5438埠口開工了。');
});

var sio = io.listen(server);
var shot = false;

sio.on('connection', function(socket) {
	socket.on('disconnect', function() {
		shot = false;
	});

	socket.on('start', function() {
        shot = true;

        takePhoto(socket);
    });
    socket.on('stop', function() {
        shot = false;


    });
});


function takePhoto(socket) {
    var cmd = 'raspistill -w 640 -h 480 -o ./www/images/photo.jpg -t 5 -q 40';
    exec(cmd, function(error, stdout, stderr) {	
      if (error != null) {
        console.log("出錯了！" + error);
        throw error;
      } else {
        console.log("拍攝完成！");
        socket.emit('liveCam', 'photo.jpg?r=' + Math.floor(Math.random() * 100000));
        
        if (shot) {
            takePhoto(socket);
        } else {
            console.log('停止拍攝。');
        }
      }
    });
}