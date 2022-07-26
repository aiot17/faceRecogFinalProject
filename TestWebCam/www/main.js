let width = 320; // 默認比例
let height = 0; // 視訊的高度，需要按照上面等比例放大

let streaming = false;

let video = null;
let canvas = null;
let photo = null;
let takePhotoButton = null;
let downloadButton = null;
let clearButton = null;

const clearPhoto = () => {
  const context = canvas.getContext('2d')
  // 生成空白照片
  context.fillStyle = "#AAA";
  context.fillRect(0, 0, canvas.width, canvas.height);
  const data = canvas.toDataURL('image/png');
  photo.setAttribute('src', data);
}

const takePhoto = () => {
  const context = canvas.getContext('2d')
  if (width && height) {
    // 將video元素的width和height拿過來
    canvas.width = width;
    canvas.height = height;

    context.drawImage(video, 0, 0, width, height);

    // 生成圖片
    const data = canvas.toDataURL('image/png');
    // console.log(data)
    photo.setAttribute('src', data);
  } else {
    clearPhoto()
  }
}

const downloadPhoto = () => {
  const link = document.createElement('a');
  link.download = 'image.png';
  link.href = canvas.toDataURL();
  link.click();
}

const start = async () => {
  video = document.getElementById('video');
  canvas = document.getElementById('canvas');
  photo = document.getElementById('photo');
  takePhotoButton = document.getElementById('takePhotoButton');
  downloadButton = document.getElementById('downloadButton');
  clearButton = document.getElementById('clearButton');

  // Fix for iOS Safari from https://leemartin.dev/hello-webrtc-on-safari-11-e8bcb5335295
  video.setAttribute('autoplay', '');
  video.setAttribute('muted', '');
  video.setAttribute('playsinline', '');
  
  // 獲取WebCam
  try {
    video.srcObject = await navigator.mediaDevices.getUserMedia({video: true, audio: false})
    video.play()
  } catch (e) {
    console.error(e)
  }

  video.addEventListener('canplay', (event) => {
    console.log("canplay event")
    if (!streaming) {
      // 按比例放大 videoHeight
      height = video.videoHeight / (video.videoWidth / width);

      // 設置 video 的寬高
      video.setAttribute('width', width);
      video.setAttribute('height', height);

      // 設置 canvas 的寬高
      canvas.setAttribute('width', width);
      canvas.setAttribute('height', height);
      streaming = true;
    }
  }, false)

  takePhotoButton.addEventListener('click', (event) => {
    // 拍照
    takePhoto()
  }, false)

  downloadButton.addEventListener('click', (event) => {
    // 下載
    downloadPhoto()
  })

  clearButton.addEventListener('click', (event) => {
    clearPhoto();
  })

  // 生成默認空白圖片
  clearPhoto();
}

start().then()