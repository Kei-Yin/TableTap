// scan.js

// 启动扫码
function startScanner() {
    alert("Sweep function activated in...");
  
    const readerElement = document.getElementById("reader");
    readerElement.style.display = "block";
  
    const html5QrCode = new Html5Qrcode("reader");
    html5QrCode.start(
      { facingMode: "environment" }, // 后置摄像头
      { fps: 10, qrbox: 250 },       // 扫码配置
      qrCodeMessage => {
        html5QrCode.stop(); // 停止摄像头
        window.location.href = qrCodeMessage; // 跳转
      },
      errorMessage => {
        // 可选：你可以在这里记录失败尝试
        console.warn("Recognition Failure:", errorMessage);
      }
    ).catch(err => {
      console.error("Camera initialisation failed:", err);
      alert("Failed to start the camera, check your browser permissions or use Safari!");
    });
  }
  