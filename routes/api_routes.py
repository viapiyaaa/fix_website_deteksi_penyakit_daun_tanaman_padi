import os
from flask import Blueprint, request, jsonify, current_app, session
from tensorflow.keras.models import load_model
from utils.image_processing import allowed_file, prepare_image
from utils.validation import validate_leaf_rice_image
from utils.chat import get_chat_response
from config import LABELS
import numpy as np

# CONFIDENCE_THRESHOLD = 0.60 

api = Blueprint('api', __name__)

MODEL_PATH = "./model/model_ini.keras"
MODEL_URL = "https://drive.google.com/file/d/1v9AaWkc9ReRKtUDkjmuROvchCVRw0M_-/view?usp=sharing"

# Download model jika belum ada
if not os.path.exists(MODEL_PATH):
    os.makedirs("model", exist_ok=True)
    print("Model not found. Downloading from Google Drive...")
    gdown.download(MODEL_URL, MODEL_PATH, quiet=False)

# Load TF model
try:
    model = load_model(MODEL_PATH)
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None


@api.route('/detect', methods=['POST'])
def detect():

    if model is None:
        return jsonify({'error': 'Model tidak tersedia'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'Tidak ada gambar yang diunggah'}), 400

    file = request.files['image']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Format file tidak didukung'}), 400

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)

    try:
        file.save(filepath)

        # GPT Vision validation
        validation_result = validate_leaf_rice_image(filepath)
        validation_result = validation_result.strip().upper()
        print(f"[VALIDATION] {validation_result}")

        if validation_result == 'INVALID':
            return jsonify({
                'status': 'INVALID',
                'message': 'Gambar yang diunggah bukan gambar penyakit tanaman padi'
            }), 400


        # Preprocess
        img_array = prepare_image(filepath)
        if img_array is None:
            raise ValueError("Gagal memproses gambar")

        # Prediction
        predictions = model.predict(img_array)
        confidence = float(np.max(predictions))           
        predicted_class = str(LABELS[np.argmax(predictions)])  

        print(f"[PREDICT] {predicted_class} ({confidence:.4f})")
        
        # final_label = validate_image(predicted_class, is_rice_leaf=True)
        # print(f"[FINAL LABEL] {final_label}")

        # Confidence threshold
        # if confidence < CONFIDENCE_THRESHOLD:
        #     return jsonify({
        #         'status': 'OUT_OF_SCOPE',
        #         'message': 'Penyakit tidak termasuk dalam kelas yang dikenali sistem',
        #         'confidence': confidence
        #     }), 422

        # Final detection (SESSION SAFE)
        detection = {
            'status': 'VALID',
            'label': predicted_class,
            'confidence': confidence
        }

        # SESSION AMAN
        history = session.get('detection_history', [])
        history.append(detection)
        session['detection_history'] = history
        session.modified = True

        return jsonify({'detections': [detection]}), 200

    except Exception as e:
        print("[ERROR DETECT]", repr(e))
        return jsonify({
            'status': 'ERROR',
            'message': 'Terjadi kesalahan saat memproses gambar',
            'detail': str(e)
        }), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@api.route('/get_response', methods=['POST'])
def get_response():
    """Handle chat response request"""
    try:
        data = request.json
        if not data:
            return jsonify({"reply": "Permintaan tidak valid"}), 400
            
        user_message = data.get('message')
        if not user_message:
            return jsonify({"reply": "Pesan tidak boleh kosong"}), 400
            
        detection_result = data.get('detection_result')
        
        # If detection_result is provided, store it as a single detection object
        if detection_result and isinstance(detection_result, dict) and 'detections' in detection_result:
            detection_obj = detection_result['detections'][0] if detection_result['detections'] else None
        else:
            detection_obj = None
        
        chat_response = get_chat_response(user_message, detection_obj)
        
        if not chat_response:
            return jsonify({"reply": "Maaf, tidak dapat memproses permintaan Anda saat ini"}), 500

        return jsonify({"reply": chat_response})

    except Exception as e:
        print(f"Error in get_response: {str(e)}")
        return jsonify({"reply": "Maaf, terjadi kesalahan dalam memproses permintaan Anda. Silakan coba lagi nanti."}), 500
