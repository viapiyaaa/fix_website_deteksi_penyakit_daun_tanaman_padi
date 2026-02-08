document.addEventListener('DOMContentLoaded', function () {
  const uploadBox = document.getElementById('uploadBox');
  const imageInput = document.getElementById('imageInput');
  const imagePreview = document.getElementById('preview');
  const detectButton = document.getElementById('detectButton');
  const loadingDiv = document.getElementById('loadingDiv');
  const uploadPlaceholder = document.getElementById('upload-placeholder');
  const homeBtn = document.getElementById('home-btn');

  const cameraContainer = document.getElementById('camera-container');
  const video = document.getElementById('video');
  const captureButton = document.getElementById('captureButton');
  const cancelCameraButton = document.getElementById('cancelCameraButton');
  const hiddenCanvas = document.getElementById('hiddenCanvas');

  const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg"];

  let uploadedFile = null;
  let stream = null;

  if (homeBtn) {
    homeBtn.addEventListener('click', () => {
      window.location.href = '/';
    });
  }

  // UPLOAD BOX CLICK
  uploadBox.addEventListener('click', () => {
    if (stream) return;

    Swal.fire({
      title: 'Pilih Metode Unggah',
      html: `
        <div class="swal2-option-grid">
          <div class="swal2-option-item" id="swal-opt-camera">
            <i class="fas fa-camera"></i>
            <b>Kamera</b>
          </div>
          <div class="swal2-option-item" id="swal-opt-file">
            <i class="fas fa-file-image"></i>
            <b>Galeri / File</b>
          </div>
        </div>
      `,
      showConfirmButton: false,
      showCloseButton: true,
      didOpen: () => {
        document.getElementById('swal-opt-camera').onclick = () => {
          Swal.close();
          requestAnimationFrame(startCamera);
        };

        document.getElementById('swal-opt-file').onclick = () => {
          Swal.close();
          imageInput.click();
          document.querySelector('.swal2-container')?.remove();

        };
      }
    });
  });

  imageInput.addEventListener('change', (e) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const file = e.target.files[0];

    if (!ALLOWED_TYPES.includes(file.type)) {
      Swal.fire({
        icon: "error",
        title: "Format Tidak Didukung",
        text: "Silakan unggah gambar JPG, JPEG, atau PNG."
      });
      imageInput.value = "";
      return;
    }

    handleImageUpload(file);
    imageInput.value = "";
  });

  // HANDLE IMAGE UPLOAD (SINGLE SOURCE)
  function handleImageUpload(file) {
    uploadedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      imagePreview.style.display = 'block';
      imagePreview.classList.add('fade-in');
      uploadPlaceholder.style.display = 'none';
      detectButton.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  // CAMERA
  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      });
      video.srcObject = stream;
      cameraContainer.style.display = 'flex';
      uploadPlaceholder.style.display = 'none';
      imagePreview.style.display = 'none';
    } catch {
      Swal.fire('Error', 'Gagal mengakses kamera', 'error');
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }
    cameraContainer.style.display = 'none';
  }

  cancelCameraButton.onclick = (e) => {
    e.stopPropagation();
    stopCamera();
    if (!uploadedFile) uploadPlaceholder.style.display = 'flex';
  };

  captureButton.onclick = (e) => {
    e.stopPropagation();

    hiddenCanvas.width = video.videoWidth;
    hiddenCanvas.height = video.videoHeight;
    hiddenCanvas.getContext('2d').drawImage(video, 0, 0);

    hiddenCanvas.toBlob((blob) => {
      const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
      handleImageUpload(file);
      stopCamera();
    }, 'image/jpeg');
  };

  // DETECT BUTTON
  detectButton.addEventListener('click', async () => {
    if (!uploadedFile) return;

    loadingDiv.style.display = 'flex';
    detectButton.disabled = true;

    const formData = new FormData();
    formData.append('image', uploadedFile);

    try {
      const response = await fetch('/detect', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok && result.detections) {
        sessionStorage.setItem('detectionResult', JSON.stringify(result));
        sessionStorage.setItem('uploadedImage', imagePreview.src);

        Swal.fire({
          icon: 'success',
          title: 'Deteksi Berhasil',
          text: 'Gambar berhasil diproses'
        }).then(() => {
          window.location.href = '/chatbot';
        });
        return;
      }

      Swal.fire('Error', result.error || 'Gambar yang diunggah bukan gambar penyakit daun tanaman padi', 'error');
    } catch {
      Swal.fire('Error', 'Gagal terhubung ke server', 'error');
    } finally {
      loadingDiv.style.display = 'none';
      detectButton.disabled = false;
    }
  });

  // DRAG & DROP
  uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#2d6a4f';
  });

  uploadBox.addEventListener('dragleave', () => {
    uploadBox.style.borderColor = '#e4e4e4';
  });

  uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#e4e4e4';

    const file = e.dataTransfer.files[0];
    if (!ALLOWED_TYPES.includes(file.type)) {
      Swal.fire({
        icon: "error",
        title: "Format Tidak Didukung",
        text: "Silakan unggah gambar JPG, JPEG, atau PNG."
      });
      return;
    }

    handleImageUpload(file);
  });
});
