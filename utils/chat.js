// Fungsi ini dipanggil setelah proses deteksi CNN selesai
async function handleDetectionSuccess(detectionData) {
  // 1. Ambil data label (misal: "Bacterialblight")
  const result = detectionData.detections[0];
  const label = result.label;

  // 2. Tampilkan di Kotak Hasil (UI yang sudah kamu punya)
  document.getElementById('result-label').innerText = label;
  document.getElementById('confidence-score').innerText = (result.confidence * 100).toFixed(1) + '%';

  // 3. TRIGGER OTOMATIS: Langsung panggil chatbot tanpa user mengetik
  console.log('Memulai inisiasi chatbot otomatis untuk label:', label);

  const autoMessage = `Saya baru saja mendeteksi ${label}. Apa yang harus saya lakukan?`;

  // Tampilkan pesan "sedang mengetik..." di UI chat
  showTypingIndicator();

  try {
    const response = await fetch('/api/get_response', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: autoMessage,
        detection_result: detectionData, // Mengirim seluruh objek deteksi ke backend
      }),
    });

    const chatData = await response.json();

    // Tampilkan balasan AI di Chat Box
    appendMessageToChat('AI Assistant', chatData.reply);
    hideTypingIndicator();
  } catch (error) {
    console.error('Gagal memicu chatbot:', error);
  }
}
