"""
src/predict_onnx.py
Modul Inferensi Berbasis ONNX Runtime (Ultra-Lightweight untuk Vercel Serverless)
Bebas dari dependensi raksasa TensorFlow, ukuran hanya ~30 MB!
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any
from PIL import Image, UnidentifiedImageError
import numpy as np
import onnxruntime as ort

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "model.onnx"
CLASS_NAMES_PATH = PROJECT_ROOT / "models" / "class_names.json"

_SESSION = None
_CLASS_NAMES = None

def get_onnx_session():
    """Singleton session caching untuk ONNX runtime."""
    global _SESSION, _CLASS_NAMES
    if _SESSION is None:
        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 2
        opts.intra_op_num_threads = 2
        _SESSION = ort.InferenceSession(str(MODEL_PATH), sess_options=opts, providers=['CPUExecutionProvider'])
    if _CLASS_NAMES is None:
        with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
            _CLASS_NAMES = json.load(f)
    return _SESSION, _CLASS_NAMES

def predict_image_onnx(image_input) -> Dict[str, Any]:
    """Menjalankan inferensi gambar menggunakan ONNX Runtime (kompatibel penuh dengan output predict_image)."""
    try:
        session, class_names = get_onnx_session()
    except Exception as e:
        return {
            "status": "ERROR",
            "predicted_class": "N/A",
            "confidence": 0.0,
            "probabilities": {},
            "gradcam_image": None,
            "error_message": f"Gagal memuat model ONNX: {str(e)}"
        }

    try:
        if isinstance(image_input, (str, Path)):
            img_path = Path(image_input)
            if not img_path.exists():
                return {
                    "status": "ERROR",
                    "predicted_class": "N/A",
                    "confidence": 0.0,
                    "probabilities": {},
                    "gradcam_image": None,
                    "error_message": f"File gambar tidak ditemukan: {img_path}"
                }
            pil_img = Image.open(img_path)
        elif isinstance(image_input, Image.Image):
            pil_img = image_input
        else:
            return {
                "status": "ERROR",
                "predicted_class": "N/A",
                "confidence": 0.0,
                "probabilities": {},
                "gradcam_image": None,
                "error_message": "Format input gambar tidak didukung."
            }

        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

    except UnidentifiedImageError:
        return {
            "status": "ERROR",
            "predicted_class": "N/A",
            "confidence": 0.0,
            "probabilities": {},
            "gradcam_image": None,
            "error_message": "File citra corrupt atau bukan format gambar yang valid."
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "predicted_class": "N/A",
            "confidence": 0.0,
            "probabilities": {},
            "gradcam_image": None,
            "error_message": f"Terjadi kesalahan saat membaca gambar: {str(e)}"
        }

    # 1. Resize ke 224x224
    img_resized = pil_img.resize((224, 224), Image.Resampling.BILINEAR)
    img_arr = np.array(img_resized, dtype=np.float32)

    # 2. Preprocessing spesifik MobileNetV2 (skala [-1, 1])
    img_arr = (img_arr / 127.5) - 1.0
    img_batch = np.expand_dims(img_arr, axis=0) # Shape: (1, 224, 224, 3)

    # 3. Inferensi ONNX
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    outputs = session.run([output_name], {input_name: img_batch})[0][0]

    # Model Dense(6, activation='softmax') menghasilkan probabilitas langsung
    probs = outputs

    pred_idx = int(np.argmax(probs))
    confidence = float(probs[pred_idx] * 100.0)
    predicted_class = class_names[pred_idx]

    probabilities = {
        class_names[i]: float(probs[i] * 100.0)
        for i in range(len(class_names))
    }
    probabilities = dict(sorted(probabilities.items(), key=lambda x: x[1], reverse=True))

    return {
        "status": "SUCCESS",
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2),
        "probabilities": {k: round(v, 2) for k, v in probabilities.items()},
        "gradcam_image": None,
        "error_message": None
    }
