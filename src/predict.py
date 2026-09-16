"""
Module predict.py
Fungsi Inferensi Citra Tunggal (FruitFresh AI)
Mendukung input gambar baru, resize 224x224, preprocessing MobileNetV2,
menghitung confidence score, probabilitas setiap class, dan error handling tangguh.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, UnidentifiedImageError
import numpy as np
import tensorflow as tf

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.preprocessing import IMAGE_SIZE

_MODEL_CACHE: Optional[tf.keras.Model] = None
_CLASS_NAMES_CACHE: Optional[list] = None

def get_model_and_classes():
    """Memuat model dan daftar nama kelas secara singleton (caching)."""
    global _MODEL_CACHE, _CLASS_NAMES_CACHE
    
    if _MODEL_CACHE is not None and _CLASS_NAMES_CACHE is not None:
        return _MODEL_CACHE, _CLASS_NAMES_CACHE
        
    models_dir = project_root / "models"
    model_path = models_dir / "best_model.keras"
    class_names_path = models_dir / "class_names.json"
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"File model tidak ditemukan di: {model_path}. "
            "Harap jalankan proses training terlebih dahulu dengan perintah: python src/train.py"
        )
        
    if not class_names_path.exists():
        raise FileNotFoundError(
            f"File daftar kelas tidak ditemukan di: {class_names_path}. "
            "Pastikan training telah selesai menyimpan metadata kelas."
        )
        
    with open(class_names_path, "r", encoding="utf-8") as f:
        _CLASS_NAMES_CACHE = json.load(f)
        
    _MODEL_CACHE = tf.keras.models.load_model(str(model_path))
    return _MODEL_CACHE, _CLASS_NAMES_CACHE

def predict_image(image_input, return_gradcam: bool = False) -> Dict[str, Any]:
    """
    Fungsi prediksi untuk citra tunggal.
    image_input dapat berupa:
    - Path string / Path object ke file gambar
    - PIL.Image object
    
    Mengembalikan dictionary:
    {
        "status": "SUCCESS" | "ERROR",
        "predicted_class": str,
        "confidence": float (persentase, misal 96.21),
        "probabilities": Dict[str, float], # { "freshapples": 96.21, ... }
        "gradcam_image": Optional[PIL.Image.Image],
        "error_message": Optional[str]
    }
    """
    try:
        model, class_names = get_model_and_classes()
    except Exception as e:
        return {
            "status": "ERROR",
            "predicted_class": "N/A",
            "confidence": 0.0,
            "probabilities": {},
            "gradcam_image": None,
            "error_message": str(e)
        }
        
    # 1. Buka dan validasi gambar
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
            
        # Konversi ke mode RGB (menangani citra RGBA atau Grayscale)
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
        
    # 2. Resize ke 224x224
    img_resized = pil_img.resize(IMAGE_SIZE, Image.Resampling.BILINEAR)
    img_array = np.array(img_resized, dtype=np.float32)
    
    # 3. Preprocessing spesifik MobileNetV2
    img_preprocessed = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    img_batch = np.expand_dims(img_preprocessed, axis=0) # Shape: (1, 224, 224, 3)
    
    # 4. Prediksi Model
    preds = model.predict(img_batch, verbose=0)[0] # Array probabilitas untuk tiap kelas
    
    pred_idx = int(np.argmax(preds))
    confidence = float(preds[pred_idx] * 100)
    predicted_class = class_names[pred_idx]
    
    # Mapping seluruh kelas beserta probabilitasnya
    probabilities = {
        class_names[i]: float(preds[i] * 100)
        for i in range(len(class_names))
    }
    
    # Urutkan probabilitas dari tertinggi ke terendah
    probabilities = dict(sorted(probabilities.items(), key=lambda x: x[1], reverse=True))
    
    # 5. Opsi Grad-CAM Overlay
    gradcam_img = None
    if return_gradcam:
        try:
            from src.gradcam import generate_gradcam_heatmap, create_gradcam_overlay
            heatmap = generate_gradcam_heatmap(img_batch, model, pred_index=pred_idx)
            gradcam_img = create_gradcam_overlay(pil_img, heatmap)
        except Exception as e:
            print(f"[WARNING] Grad-CAM gagal digenerate: {e}")
            
    return {
        "status": "SUCCESS",
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2),
        "probabilities": {k: round(v, 2) for k, v in probabilities.items()},
        "gradcam_image": gradcam_img,
        "error_message": None
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(f"[INFO] Melakukan inferensi untuk: {test_file}")
        res = predict_image(test_file)
        if res["status"] == "SUCCESS":
            print("=" * 50)
            print(f"Prediksi   : {res['predicted_class']}")
            print(f"Confidence : {res['confidence']}%")
            print("-" * 50)
            print("Probabilitas Seluruh Kelas:")
            for cls, prob in res['probabilities'].items():
                print(f"  • {cls:<20} : {prob:>6.2f}%")
            print("=" * 50)
        else:
            print(f"[ERROR] {res['error_message']}")
    else:
        print("Penggunaan: python src/predict.py <path_ke_file_gambar>")
