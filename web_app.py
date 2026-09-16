"""
web_app.py - FruitFresh AI Flask Application
Web server mandiri berbasis Flask yang mengimplementasikan antarmuka identik
dengan referensi video TikTok @devilda_id untuk Klasifikasi Kesegaran Buah.
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
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from src.predict import predict_image, get_model_and_classes

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "templates"),
    static_folder=str(PROJECT_ROOT / "static")
)
CORS(app)

# Dictionary metadata informasi buah dan rekomendasi kualitas industri
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
        "recommendation": "Sangat aman dan berkhasiat tinggi untuk dikonsumsi langsung, dibuat jus segar, atau dipadukan dalam salad sehat.",
        "storage_tip": "Simpan di laci sayur kulkas (crisper) 1-4°C. Jauhkan dari sayuran berdaun hijau karena emisi etilen apel dapat mempercepat pelayuan sayuran."
    },
    "rottenapples": {
        "title": "Rotten Apple (Apel Rusak / Busuk)",
        "condition": "Busuk / Rusak",
        "fruit_type": "Apel",
        "is_fresh": False,
        "icon": "🍎",
        "theme_color": "#ef4444",
        "description": "Apel telah mengalami dekomposisi jaringan organik dengan bercak kecokelatan melunak (soft rot), penurunan kelembapan drastis, serta risiko kontaminasi mikotoksin patogen seperti patulin (Penicillium expansum).",
        "shelf_life": "0 Hari (Kadaluarsa / Rusak)",
        "optimal_temp": "Isolasi Suhu Ruang Terbuka",
        "humidity_rh": "N/A (Cegah Kelembaban)",
        "ethylene_level": "Pelepasan Etilen Abnormal",
        "qc_action": "TOLAK QC. Segera musnahkan atau alihkan ke fasilitas pengomposan limbah organik.",
        "aroma_texture": "Aroma asam fermentasi menyengat, tekstur lembek berair dan berpori busuk.",
        "recommendation": "TIDAK LAYAK KONSUMSI. Memakan apel yang busuk berisiko menyebabkan gangguan pencernaan dan infeksi mikotoksin patulin.",
        "storage_tip": "Segera pisahkan dan buang agar spora pembusukan tidak mengontaminasi krat buah segar lainnya di sekitarnya."
    },
    "freshbanana": {
        "title": "Fresh Banana (Pisang Segar)",
        "condition": "Segar",
        "fruit_type": "Pisang",
        "is_fresh": True,
        "icon": "🍌",
        "theme_color": "#10b981",
        "description": "Pisang berada pada tingkat kematangan optimal (Cavendish Stage 5-6) dengan kulit kuning cerah merata, bebas dari memar dalam, dan memiliki kadar gula alami serta kalium yang seimbang.",
        "shelf_life": "4 - 7 Hari (Suhu Ruang 13-15°C)",
        "optimal_temp": "13°C - 15°C (Hindari <12°C)",
        "humidity_rh": "85% - 90% RH",
        "ethylene_level": "Tinggi (Klimakterik Aktif)",
        "qc_action": "LOLOS QC GRADE A. Siap untuk penjualan ritel harian atau konsumsi segar.",
        "aroma_texture": "Aroma harum manis khas pisang matang, tekstur lembut padat dan tidak lembek.",
        "recommendation": "Sangat baik untuk konsumsi harian, sumber energi cepat untuk olahraga, atau bahan smoothie alami.",
        "storage_tip": "Gantung tandan atau bungkus pangkal batang (crown) dengan plastic wrap untuk memperlambat pelepasan etilen. JANGAN simpan di kulkas di bawah 12°C untuk menghindari chilling injury (kulit menghitam)."
    },
    "rottenbanana": {
        "title": "Rotten Banana (Pisang Busuk)",
        "condition": "Busuk / Rusak",
        "fruit_type": "Pisang",
        "is_fresh": False,
        "icon": "🍌",
        "theme_color": "#ef4444",
        "description": "Pisang mengalami pembusukan lanjut dengan kulit menghitam menyeluruh, degradasi jaringan seluler, serta aktivitas fermentasi anaerobik yang menghasilkan rasa dan bau asam berlebih.",
        "shelf_life": "0 Hari (Masa Edar Berakhir)",
        "optimal_temp": "N/A (Karantina)",
        "humidity_rh": "N/A",
        "ethylene_level": "Pelepasan Gas Etilen Ekstrem",
        "qc_action": "TOLAK QC. Pisahkan dari area sortir untuk mencegah pembusukan silang.",
        "aroma_texture": "Aroma tajam beralkohol/fermentasi, tekstur sangat lembek berair dan menghitam di bagian dalam.",
        "recommendation": "Jika hanya overripe berbintik tanpa jamur kapang putih/hijau, dapat diolah menjadi bolu pisang (banana bread). Jika berlendir dan berbau tajam, wajib dibuang.",
        "storage_tip": "Jauhkan dari komoditas buah lain karena pisang busuk melepaskan gas etilen dalam jumlah sangat tinggi yang mempercepat kebusukan buah sekitarnya."
    },
    "freshoranges": {
        "title": "Fresh Orange (Jeruk Segar)",
        "condition": "Segar",
        "fruit_type": "Jeruk",
        "is_fresh": True,
        "icon": "🍊",
        "theme_color": "#10b981",
        "description": "Jeruk dalam kondisi segar prima dengan pori-pori kulit kencang, warna oranye cerah, dan bobot mantap berisi bulir air jeruk kaya sari vitamin C, flavonoid, dan mineral esensial.",
        "shelf_life": "2 - 3 Minggu (Kulkas 4-7°C) / 7 - 10 Hari (Suhu Ruang)",
        "optimal_temp": "4°C - 7°C",
        "humidity_rh": "85% - 90% RH",
        "ethylene_level": "Rendah (Non-Klimakterik)",
        "qc_action": "LOLOS QC GRADE A. Bobot sari buah prima, siap distribusi ritel.",
        "aroma_texture": "Aroma citrus khas yang tajam menyegarkan, kulit kencang elastis dan tidak kusam.",
        "recommendation": "Sangat dianjurkan untuk dikonsumsi langsung atau diperas menjadi jus murni kaya vitamin penambah imunitas tubuh.",
        "storage_tip": "Simpan pada tempat berventilasi baik. Hindari kantong plastik tertutup rapat agar tidak lembap dan mencegah tumbuhnya kapang biru/hijau."
    },
    "rottenoranges": {
        "title": "Rotten Orange (Jeruk Rusak / Busuk)",
        "condition": "Busuk / Rusak",
        "fruit_type": "Jeruk",
        "is_fresh": False,
        "icon": "🍊",
        "theme_color": "#ef4444",
        "description": "Jeruk mengalami kerusakan patologis yang umumnya disebabkan oleh jamur Penicillium digitatum (green mold) atau Penicillium italicum (blue mold), disertai jaringan buah yang mengering atau lembek berlendir.",
        "shelf_life": "0 Hari (Terkontaminasi Spora Kapang)",
        "optimal_temp": "Karantina / Pemusnahan",
        "humidity_rh": "N/A",
        "ethylene_level": "N/A",
        "qc_action": "TOLAK QC & SANITASI. Segera bersihkan wadah penyimpanan dengan larutan disinfektan.",
        "aroma_texture": "Aroma apak berjamur atau asam busuk, tekstur kulit melunak kempes dengan serbuk spora kehijauan/putih.",
        "recommendation": "SANGAT BERBAHAYA JIKA DIKONSUMSI. Spora jamur dapat menembus bulir dalam dan memicu reaksi alergi serta mikotoksikosis.",
        "storage_tip": "Segera bungkus rapat dan buang ke tempat sampah luar ruangan untuk menghindari penyebaran spora terbang ke buah lainnya."
    }
}

# Warm up model saat server di-boot
print("[FruitFresh AI] Memuat model MobileNetV2 dan metadata...")
try:
    _m, _c = get_model_and_classes()
    print(f"[FruitFresh AI] Model berhasil dimuat! Kelas terdaftar: {_c}")
except Exception as e:
    print(f"[FruitFresh AI] Peringatan: {e}")

@app.route("/")
def index():
    """Halaman utama FruitFresh AI."""
    return render_template("index.html")

@app.route("/health")
def health():
    """Endpoint status server & model."""
    return jsonify({
        "status": "healthy",
        "model": "MobileNetV2 (Transfer Learning & Fine-Tuning)",
        "test_accuracy": "97.40%",
        "test_f1_score": "97.43%",
        "dataset_total": 13599,
        "classes": list(FRUIT_METADATA.keys())
    })

@app.route("/predict", methods=["POST"])
@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Endpoint utama inferensi citra buah.
    Mendukung upload multipart/form-data (key: 'image')
    atau JSON payload dengan sample path / base64 string.
    """
    start_time = time.time()
    pil_img = None
    
    # 1. Cek upload via form-data
    if "image" in request.files:
        file = request.files["image"]
        if file.filename != "":
            try:
                pil_img = Image.open(file.stream)
            except Exception as e:
                return jsonify({"status": "ERROR", "error_message": f"Format citra tidak valid: {e}"}), 400
                
    # 2. Cek payload JSON (sample atau base64)
    if pil_img is None and request.is_json:
        data = request.get_json()
        if "sample" in data:
            sample_name = data["sample"] # misal 'fresh_apple.png'
            sample_path = PROJECT_ROOT / "static" / "samples" / sample_name
            if sample_path.exists():
                pil_img = Image.open(sample_path)
            else:
                return jsonify({"status": "ERROR", "error_message": f"Sample tidak ditemukan: {sample_name}"}), 404
        elif "image_base64" in data:
            try:
                b64_str = data["image_base64"]
                if "," in b64_str:
                    b64_str = b64_str.split(",", 1)[1]
                img_bytes = base64.b64decode(b64_str)
                pil_img = Image.open(io.BytesIO(img_bytes))
            except Exception as e:
                return jsonify({"status": "ERROR", "error_message": f"Gagal decode base64: {e}"}), 400

    if pil_img is None:
        return jsonify({
            "status": "ERROR",
            "error_message": "Tidak ada gambar yang disediakan. Unggah file gambar atau pilih sampel."
        }), 400

    # 3. Jalankan inferensi dengan Grad-CAM
    try:
        res = predict_image(pil_img, return_gradcam=True)
    except Exception as e:
        return jsonify({"status": "ERROR", "error_message": f"Kesalahan inferensi: {e}"}), 500

    if res.get("status") != "SUCCESS":
        return jsonify(res), 500

    # 4. Hitung latensi & metadata buah
    elapsed_ms = round((time.time() - start_time) * 1000, 1)
    predicted_key = res["predicted_class"]
    meta = FRUIT_METADATA.get(predicted_key, {
        "title": predicted_key,
        "condition": "Terdeteksi",
        "fruit_type": "Buah",
        "is_fresh": "fresh" in predicted_key.lower(),
        "icon": "🍏",
        "theme_color": "#16a34a" if "fresh" in predicted_key.lower() else "#dc2626",
        "description": "Hasil analisis klasifikasi citra buah oleh sistem deep learning.",
        "shelf_life": "Periksa kondisi fisik buah secara berkala.",
        "aroma_texture": "Sesuai indikator visual model.",
        "recommendation": "Lakukan pengecekan menyeluruh sebelum mengonsumsi.",
        "storage_tip": "Simpan pada tempat yang bersih dan higienis."
    })

    # 5. Konversi Grad-CAM ke Base64 jika ada
    gradcam_b64 = None
    if res.get("gradcam_image") is not None:
        try:
            buf = io.BytesIO()
            res["gradcam_image"].save(buf, format="JPEG", quality=90)
            gradcam_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
        except Exception as e:
            print(f"[WARNING] Gagal encoding Grad-CAM: {e}")

    # Konversi citra asli yang telah diproses ke thumbnail base64 untuk display instan
    orig_b64 = None
    try:
        buf_orig = io.BytesIO()
        # Resize thumbnail jika terlalu besar
        thumb = pil_img.copy()
        thumb.thumbnail((600, 600))
        if thumb.mode != "RGB":
            thumb = thumb.convert("RGB")
        thumb.save(buf_orig, format="JPEG", quality=85)
        orig_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf_orig.getvalue()).decode('utf-8')}"
    except Exception:
        pass

    return jsonify({
        "status": "SUCCESS",
        "predicted_class": predicted_key,
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
        "gradcam_image": gradcam_b64
    })

@app.route("/samples", methods=["GET"])
def get_samples():
    """Daftar sampel gambar buah untuk pengetesan instan 1-klik."""
    samples = [
        {"id": "fresh_apple", "file": "fresh_apple.png", "name": "Fresh Apple", "class": "freshapples", "icon": "🍏", "type": "Apel Segar"},
        {"id": "rotten_apple", "file": "rotten_apple.png", "name": "Rotten Apple", "class": "rottenapples", "icon": "🍎", "type": "Apel Busuk"},
        {"id": "fresh_banana", "file": "fresh_banana.png", "name": "Fresh Banana", "class": "freshbanana", "icon": "🍌", "type": "Pisang Segar"},
        {"id": "rotten_banana", "file": "rotten_banana.png", "name": "Rotten Banana", "class": "rottenbanana", "icon": "🍌", "type": "Pisang Busuk"},
        {"id": "fresh_orange", "file": "fresh_orange.png", "name": "Fresh Orange", "class": "freshoranges", "icon": "🍊", "type": "Jeruk Segar"},
        {"id": "rotten_orange", "file": "rotten_orange.png", "name": "Rotten Orange", "class": "rottenoranges", "icon": "🍊", "type": "Jeruk Busuk"}
    ]
    return jsonify({"status": "SUCCESS", "samples": samples})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5005))
    print("\n=======================================================")
    print(" [FruitFresh AI] Web Application Server Running")
    print(" Terinspirasi dari Referensi TikTok @devilda_id")
    print(f" URL Akses Lokal : http://127.0.0.1:{port}")
    print("=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
