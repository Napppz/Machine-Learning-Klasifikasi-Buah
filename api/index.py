"""
api/index.py - Vercel Serverless Function Entry Point for FruitFresh AI
Menggunakan ONNX Runtime Ultra-Lightweight (~30 MB)
100% Kompatibel dengan batasan Serverless Vercel (Ukuran Unzipped < 250 MB)
"""

import os
import sys
import io
import time
import base64
import json
from pathlib import Path
from PIL import Image
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Tambahkan root workspace ke sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.predict_onnx import predict_image_onnx

template_dir = CURRENT_DIR / "templates" if (CURRENT_DIR / "templates").exists() else PROJECT_ROOT / "templates"
static_dir = CURRENT_DIR / "static" if (CURRENT_DIR / "static").exists() else PROJECT_ROOT / "static"

app = Flask(
    __name__,
    template_folder=str(template_dir),
    static_folder=str(static_dir)
)
CORS(app)

# Dictionary metadata informasi buah dan rekomendasi industri
FRUIT_METADATA = {
    "freshapples": {
        "title": "Fresh Apple (Apel Segar)",
        "condition": "Segar",
        "fruit_type": "Apel",
        "is_fresh": True,
        "icon": "🍏",
        "theme_color": "#10b981",
        "description": "Apel berada dalam kondisi prima dengan kulit kencang mulus, tekstur daging renyah, dan aroma manis asam yang segar. Kandungan antioksidan (quercetin), vitamin C, dan serat pangan masih optimal.",
        "shelf_life": "3 - 4 Minggu (Kulkas) / 5 - 7 Hari (Suhu Ruang)",
        "optimal_temp": "1°C - 4°C",
        "humidity_rh": "90% - 95% RH",
        "ethylene_level": "Tinggi (High Ethylene Producer)",
        "qc_action": "LOLOS QC GRADE A. Sangat layak didistribusikan ke etalase ritel atau dikonsumsi langsung.",
        "aroma_texture": "Aroma segar manis alami, tekstur padat renyah tanpa memar.",
        "recommendation": "Sangat aman dan berkhasiat tinggi untuk dikonsumsi langsung, dibuat jus segar, atau salad.",
        "storage_tip": "Simpan di laci sayur kulkas (crisper) 1-4°C. Jauhkan dari sayuran berdaun hijau."
    },
    "rottenapples": {
        "title": "Rotten Apple (Apel Rusak / Busuk)",
        "condition": "Busuk / Rusak",
        "fruit_type": "Apel",
        "is_fresh": False,
        "icon": "🍎",
        "theme_color": "#ef4444",
        "description": "Apel telah mengalami dekomposisi jaringan organik dengan bercak kecokelatan melunak (soft rot) dan risiko kontaminasi patogen.",
        "shelf_life": "0 Hari (Kadaluarsa / Rusak)",
        "optimal_temp": "Isolasi Suhu Ruang",
        "humidity_rh": "N/A",
        "ethylene_level": "Pelepasan Etilen Abnormal",
        "qc_action": "TOLAK QC. Segera musnahkan atau alihkan ke fasilitas pengomposan limbah organik.",
        "aroma_texture": "Aroma asam fermentasi menyengat, tekstur lembek berair.",
        "recommendation": "TIDAK LAYAK KONSUMSI.",
        "storage_tip": "Segera pisahkan dan buang agar spora tidak mengontaminasi krat buah lain."
    },
    "freshbanana": {
        "title": "Fresh Banana (Pisang Segar)",
        "condition": "Segar",
        "fruit_type": "Pisang",
        "is_fresh": True,
        "icon": "🍌",
        "theme_color": "#10b981",
        "description": "Pisang berada pada tingkat kematangan optimal (Cavendish Stage 5-6) dengan kulit kuning cerah merata dan bebas memar dalam.",
        "shelf_life": "4 - 7 Hari (Suhu Ruang 13-15°C)",
        "optimal_temp": "13°C - 15°C (Hindari <12°C)",
        "humidity_rh": "85% - 90% RH",
        "ethylene_level": "Tinggi (Klimakterik Aktif)",
        "qc_action": "LOLOS QC GRADE A. Siap untuk penjualan ritel harian atau konsumsi segar.",
        "aroma_texture": "Aroma harum manis khas pisang matang, tekstur lembut padat.",
        "recommendation": "Sangat baik untuk konsumsi harian dan sumber energi cepat.",
        "storage_tip": "Bungkus pangkal batang (crown) dengan plastic wrap. JANGAN simpan di kulkas di bawah 12°C."
    },
    "rottenbanana": {
        "title": "Rotten Banana (Pisang Busuk)",
        "condition": "Busuk / Rusak",
        "fruit_type": "Pisang",
        "is_fresh": False,
        "icon": "🍌",
        "theme_color": "#ef4444",
        "description": "Pisang mengalami pembusukan lanjut dengan kulit menghitam menyeluruh dan degradasi seluler.",
        "shelf_life": "0 Hari (Masa Edar Berakhir)",
        "optimal_temp": "N/A (Karantina)",
        "humidity_rh": "N/A",
        "ethylene_level": "Pelepasan Gas Etilen Ekstrem",
        "qc_action": "TOLAK QC. Pisahkan dari area sortir untuk mencegah pembusukan silang.",
        "aroma_texture": "Aroma tajam beralkohol/fermentasi, tekstur sangat lembek berair.",
        "recommendation": "Jika overripe berbintik tanpa jamur dapat diolah jadi bolu pisang. Jika berlendir, buang.",
        "storage_tip": "Jauhkan dari buah lain karena emisi gas etilen sangat tinggi."
    },
    "freshoranges": {
        "title": "Fresh Orange (Jeruk Segar)",
        "condition": "Segar",
        "fruit_type": "Jeruk",
        "is_fresh": True,
        "icon": "🍊",
        "theme_color": "#10b981",
        "description": "Jeruk dalam kondisi segar prima dengan pori-pori kulit kencang, warna oranye cerah, dan bulir air berlimpah.",
        "shelf_life": "2 - 3 Minggu (Kulkas 4-7°C) / 7 - 10 Hari (Suhu Ruang)",
        "optimal_temp": "4°C - 7°C",
        "humidity_rh": "85% - 90% RH",
        "ethylene_level": "Rendah (Non-Klimakterik)",
        "qc_action": "LOLOS QC GRADE A. Bobot sari buah prima, siap distribusi ritel.",
        "aroma_texture": "Aroma citrus tajam menyegarkan, kulit kencang elastis.",
        "recommendation": "Sangat dianjurkan untuk dikonsumsi langsung atau diperas menjadi jus murni.",
        "storage_tip": "Simpan pada tempat berventilasi baik. Hindari kantong plastik tertutup rapat."
    },
    "rottenoranges": {
        "title": "Rotten Orange (Jeruk Rusak / Busuk)",
        "condition": "Busuk / Rusak",
        "fruit_type": "Jeruk",
        "is_fresh": False,
        "icon": "🍊",
        "theme_color": "#ef4444",
        "description": "Jeruk mengalami kerusakan patologis akibat jamur Penicillium (green/blue mold) berlendir.",
        "shelf_life": "0 Hari (Terkontaminasi Spora Kapang)",
        "optimal_temp": "Karantina / Pemusnahan",
        "humidity_rh": "N/A",
        "ethylene_level": "N/A",
        "qc_action": "TOLAK QC & SANITASI. Bersihkan wadah penyimpanan dengan disinfektan.",
        "aroma_texture": "Aroma apak berjamur atau asam busuk, kulit kempes berlendir.",
        "recommendation": "SANGAT BERBAHAYA JIKA DIKONSUMSI.",
        "storage_tip": "Bungkus rapat dan buang untuk menghindari penyebaran spora terbang."
    }
}

def handle_samples():
    samples = [
        {"id": "fresh_apple", "file": "fresh_apple.png", "name": "Fresh Apple", "class": "freshapples", "icon": "🍏", "type": "Apel Segar"},
        {"id": "rotten_apple", "file": "rotten_apple.png", "name": "Rotten Apple", "class": "rottenapples", "icon": "🍎", "type": "Apel Busuk"},
        {"id": "fresh_banana", "file": "fresh_banana.png", "name": "Fresh Banana", "class": "freshbanana", "icon": "🍌", "type": "Pisang Segar"},
        {"id": "rotten_banana", "file": "rotten_banana.png", "name": "Rotten Banana", "class": "rottenbanana", "icon": "🍌", "type": "Pisang Busuk"},
        {"id": "fresh_orange", "file": "fresh_orange.png", "name": "Fresh Orange", "class": "freshoranges", "icon": "🍊", "type": "Jeruk Segar"},
        {"id": "rotten_orange", "file": "rotten_orange.png", "name": "Rotten Orange", "class": "rottenoranges", "icon": "🍊", "type": "Jeruk Busuk"}
    ]
    return jsonify({"status": "SUCCESS", "samples": samples})

def handle_predict():
    start_time = time.perf_counter()
    image_to_predict = None
    orig_b64 = None

    # Kasus 1: Upload file multipart
    if "image" in request.files:
        file = request.files["image"]
        if file.filename != "":
            file_bytes = file.read()
            image_to_predict = Image.open(io.BytesIO(file_bytes))
            orig_b64 = "data:image/jpeg;base64," + base64.b64encode(file_bytes).decode("utf-8")

    # Kasus 2: JSON payload
    if image_to_predict is None and request.is_json:
        payload = request.get_json()
        if "sample" in payload:
            sample_name = payload["sample"]
            sample_path = CURRENT_DIR / "static" / "samples" / sample_name if (CURRENT_DIR / "static" / "samples" / sample_name).exists() else PROJECT_ROOT / "static" / "samples" / sample_name
            if sample_path.exists():
                image_to_predict = Image.open(sample_path)
                with open(sample_path, "rb") as f:
                    orig_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
        elif "image_base64" in payload:
            b64_str = payload["image_base64"]
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
            raw_data = base64.b64decode(b64_str)
            image_to_predict = Image.open(io.BytesIO(raw_data))
            orig_b64 = payload["image_base64"]

    if image_to_predict is None:
        return jsonify({
            "status": "ERROR",
            "error_message": "Gambar tidak ditemukan. Harap unggah file atau pilih sampel."
        }), 400

    # Jalankan Inferensi ONNX
    res = predict_image_onnx(image_to_predict)

    if res["status"] == "ERROR":
        return jsonify(res), 500

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 1)
    pred_class = res["predicted_class"]
    meta = FRUIT_METADATA.get(pred_class, {
        "title": pred_class.replace('_', ' ').title(),
        "condition": "Segar" if "fresh" in pred_class else "Busuk",
        "fruit_type": "Buah",
        "is_fresh": "fresh" in pred_class,
        "icon": "🍏",
        "theme_color": "#10b981",
        "description": "Klasifikasi terdeteksi.",
        "shelf_life": "N/A",
        "optimal_temp": "Suhu Ruang",
        "humidity_rh": "85% - 90%",
        "ethylene_level": "Sedang",
        "qc_action": "Inspeksi selesai.",
        "aroma_texture": "Normal",
        "recommendation": "Sesuai kebutuhan.",
        "storage_tip": "Simpan di tempat berventilasi baik."
    })

    return jsonify({
        "status": "SUCCESS",
        "predicted_class": pred_class,
        "display_name": meta["title"],
        "condition": meta["condition"],
        "fruit_type": meta["fruit_type"],
        "is_fresh": meta["is_fresh"],
        "icon": meta["icon"],
        "theme_color": meta["theme_color"],
        "confidence": res["confidence"],
        "is_ood": res["confidence"] < 60.0,
        "rejection_threshold": 60.0,
        "probabilities": res["probabilities"],
        "latency_ms": elapsed_ms,
        "metadata": meta,
        "original_image": orig_b64,
        "gradcam_image": None
    })

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    if "debug" in request.url or "debug" in path or request.args.get("debug"):
        return jsonify({
            "path": path,
            "request.path": request.path,
            "request.url": request.url,
            "headers": dict(request.headers),
            "environ": {k: str(v) for k, v in request.environ.items() if isinstance(v, (str, int, float, bool))}
        })
    clean = path.strip("/").lower()
    
    # Endpoint Predict
    if clean.endswith("predict"):
        if request.method == "POST":
            return handle_predict()
        return jsonify({"status": "ERROR", "message": "Method POST required"}), 405
        
    # Endpoint Samples
    if clean.endswith("samples"):
        return handle_samples()
        
    # Static Assets (Fallback)
    if "static/" in clean:
        filename = path.split("static/", 1)[1]
        target = CURRENT_DIR / "static" if (CURRENT_DIR / "static").exists() else PROJECT_ROOT / "static"
        return send_from_directory(str(target), filename)
        
    # Landing Page
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)

