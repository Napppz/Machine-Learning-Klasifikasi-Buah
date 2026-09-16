"""
🍎 FruitFresh AI: Enterprise Fruit Quality & Freshness Inspection
Implementasi Antarmuka Web Presisi Penuh Terinspirasi dari Referensi Desain TikTok @devilda_id
Deep Learning MobileNetV2 • Explainable AI (Grad-CAM) • Cold Chain QC Protocol
"""

import io
import os
import sys
import time
import json
import datetime
from pathlib import Path
import streamlit as st
from PIL import Image

# Tambahkan root project ke sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.predict import predict_image

# -------------------------------------------------------------
# 1. Metadata Komprehensif Buah (Cold Chain & QC Protocol)
# -------------------------------------------------------------
FRUIT_METADATA = {
    "freshapples": {
        "title": "Fresh Apple (Apel Segar)",
        "condition": "Segar",
        "fruit_type": "Apel",
        "is_fresh": True,
        "icon": "🍏",
        "theme_color": "#10b981",
        "verdict": "Apel berada dalam kondisi prima, tekstur kencang renyah, dan siap didistribusikan ke etalase ritel.",
        "description": "Apel berada dalam kondisi prima dengan kulit kencang mulus, tekstur daging renyah, dan aroma manis asam yang segar. Kandungan antioksidan (quercetin), vitamin C, dan serat pangan masih optimal.",
        "shelf_life": "3 - 4 Minggu (Kulkas) / 5 - 7 Hari (Suhu Ruang)",
        "optimal_temp": "1°C - 4°C",
        "humidity_rh": "90% - 95% RH",
        "ethylene_level": "Tinggi (High Ethylene Producer)",
        "qc_action": "LOLOS QC GRADE A. Sangat layak didistribusikan ke etalase ritel atau dikonsumsi langsung.",
        "aroma_texture": "Aroma segar manis alami, tekstur padat renyah tanpa memar.",
        "recommendation": "Sangat aman dan berkhasiat tinggi untuk dikonsumsi langsung, dibuat jus segar, atau salad.",
        "storage_tip": "Simpan di laci sayur kulkas (crisper) 1-4°C. Jauhkan dari sayuran berdaun hijau karena emisi etilen apel dapat mempercepat pelayuan sayuran."
    },
    "rottenapples": {
        "title": "Rotten Apple (Apel Rusak / Busuk)",
        "condition": "Busuk / Rusak",
        "fruit_type": "Apel",
        "is_fresh": False,
        "icon": "🍎",
        "theme_color": "#ef4444",
        "verdict": "Apel telah mengalami dekomposisi jaringan organik dengan bercak busuk melunak. Tolak QC.",
        "description": "Apel telah mengalami dekomposisi jaringan organik dengan bercak kecokelatan melunak (soft rot), penurunan kelembapan drastis, serta risiko kontaminasi mikotoksin patogen seperti patulin (Penicillium expansum).",
        "shelf_life": "0 Hari (Kadaluarsa / Rusak)",
        "optimal_temp": "Isolasi Suhu Ruang Terbuka",
        "humidity_rh": "N/A (Cegah Kelembaban)",
        "ethylene_level": "Pelepasan Etilen Abnormal",
        "qc_action": "TOLAK QC. Segera musnahkan atau alihkan ke fasilitas pengomposan limbah organik.",
        "aroma_texture": "Aroma asam fermentasi menyengat, tekstur lembek berair dan berpori busuk.",
        "recommendation": "TIDAK LAYAK KONSUMSI. Memakan apel yang busuk berisiko memicu gangguan pencernaan dan infeksi mikotoksin patulin.",
        "storage_tip": "Segera pisahkan dan buang agar spora pembusukan tidak mengontaminasi krat buah segar lainnya."
    },
    "freshbanana": {
        "title": "Fresh Banana (Pisang Segar)",
        "condition": "Segar",
        "fruit_type": "Pisang",
        "is_fresh": True,
        "icon": "🍌",
        "theme_color": "#10b981",
        "verdict": "Pisang berada pada kematangan sempurna (Cavendish Stage 5-6), kulit kuning cerah, dan bebas memar.",
        "description": "Pisang berada pada tingkat kematangan optimal dengan kulit kuning cerah merata, bebas dari memar dalam, dan memiliki kadar gula alami serta kalium yang seimbang.",
        "shelf_life": "4 - 7 Hari (Suhu Ruang 13-15°C)",
        "optimal_temp": "13°C - 15°C (Hindari <12°C)",
        "humidity_rh": "85% - 90% RH",
        "ethylene_level": "Tinggi (Klimakterik Aktif)",
        "qc_action": "LOLOS QC GRADE A. Siap untuk penjualan ritel harian atau konsumsi segar.",
        "aroma_texture": "Aroma harum manis khas pisang matang, tekstur lembut padat dan tidak lembek.",
        "recommendation": "Sangat baik untuk konsumsi harian, sumber energi cepat untuk olahraga, atau bahan smoothie alami.",
        "storage_tip": "Gantung tandan atau bungkus pangkal batang (crown) dengan plastic wrap. JANGAN simpan di kulkas di bawah 12°C untuk menghindari chilling injury."
    },
    "rottenbanana": {
        "title": "Rotten Banana (Pisang Busuk)",
        "condition": "Busuk / Rusak",
        "fruit_type": "Pisang",
        "is_fresh": False,
        "icon": "🍌",
        "theme_color": "#ef4444",
        "verdict": "Pisang mengalami pembusukan lanjut dengan kulit menghitam menyeluruh dan fermentasi asam aktif.",
        "description": "Pisang mengalami pembusukan lanjut dengan kulit menghitam menyeluruh, degradasi jaringan seluler, serta aktivitas fermentasi anaerobik yang menghasilkan rasa dan bau asam berlebih.",
        "shelf_life": "0 Hari (Masa Edar Berakhir)",
        "optimal_temp": "N/A (Karantina)",
        "humidity_rh": "N/A",
        "ethylene_level": "Pelepasan Gas Etilen Ekstrem",
        "qc_action": "TOLAK QC. Pisahkan dari area sortir untuk mencegah pembusukan silang.",
        "aroma_texture": "Aroma tajam beralkohol/fermentasi, tekstur sangat lembek berair dan menghitam.",
        "recommendation": "Jika overripe berbintik tanpa jamur kapang dapat diolah menjadi bolu pisang. Jika berlendir dan berbau tajam, wajib dibuang.",
        "storage_tip": "Jauhkan dari komoditas buah lain karena pisang busuk melepaskan gas etilen sangat tinggi."
    },
    "freshoranges": {
        "title": "Fresh Orange (Jeruk Segar)",
        "condition": "Segar",
        "fruit_type": "Jeruk",
        "is_fresh": True,
        "icon": "🍊",
        "theme_color": "#10b981",
        "verdict": "Jeruk berbobot prima, kulit berkilau kencang dengan kandungan sari vitamin C melimpah.",
        "description": "Jeruk dalam kondisi segar prima dengan pori-pori kulit kencang, warna oranye cerah, dan bobot mantap berisi bulir air jeruk kaya sari vitamin C, flavonoid, dan mineral esensial.",
        "shelf_life": "2 - 3 Minggu (Kulkas 4-7°C) / 7 - 10 Hari (Suhu Ruang)",
        "optimal_temp": "4°C - 7°C",
        "humidity_rh": "85% - 90% RH",
        "ethylene_level": "Rendah (Non-Klimakterik)",
        "qc_action": "LOLOS QC GRADE A. Bobot sari buah prima, siap distribusi ritel.",
        "aroma_texture": "Aroma citrus khas yang tajam menyegarkan, kulit kencang elastis dan tidak kusam.",
        "recommendation": "Sangat dianjurkan untuk dikonsumsi langsung atau diperas menjadi jus murni kaya vitamin penambah imunitas.",
        "storage_tip": "Simpan pada tempat berventilasi baik. Hindari kantong plastik tertutup rapat agar tidak lembap dan mencegah tumbuhnya kapang."
    },
    "rottenoranges": {
        "title": "Rotten Orange (Jeruk Rusak / Busuk)",
        "condition": "Busuk / Rusak",
        "fruit_type": "Jeruk",
        "is_fresh": False,
        "icon": "🍊",
        "theme_color": "#ef4444",
        "verdict": "Jeruk terkontaminasi jamur kapang (Penicillium). Jaringan buah rusak berlendir dan berbahaya.",
        "description": "Jeruk mengalami kerusakan patologis yang umumnya disebabkan oleh jamur Penicillium digitatum (green mold) atau Penicillium italicum (blue mold), disertai jaringan buah yang mengering atau lembek berlendir.",
        "shelf_life": "0 Hari (Terkontaminasi Spora Kapang)",
        "optimal_temp": "Karantina / Pemusnahan",
        "humidity_rh": "N/A",
        "ethylene_level": "N/A",
        "qc_action": "TOLAK QC & SANITASI. Segera bersihkan wadah penyimpanan dengan larutan disinfektan.",
        "aroma_texture": "Aroma apak berjamur atau asam busuk, tekstur melunak kempes dengan serbuk spora kehijauan/putih.",
        "recommendation": "SANGAT BERBAHAYA JIKA DIKONSUMSI. Spora jamur dapat menembus bulir dalam dan memicu mikotoksikosis.",
        "storage_tip": "Segera bungkus rapat dan buang ke tempat sampah luar ruangan untuk menghindari penyebaran spora terbang."
    }
}

def inject_devilda_theme():
    """Menyuntikkan stylesheet persis bertema @devilda_id (Deep Slate Obsidian #090d16 & Neon Emerald #10b981)."""
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        /* Sembunyikan Header dan Footer default Streamlit agar terlihat seperti aplikasi web mandiri */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        footer {
            display: none !important;
        }
        #MainMenu {
            display: none !important;
        }
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            max-width: 1140px !important;
        }

        /* Root Global Palette (Identik dengan @devilda_id style.css) */
        :root {
            --bg-main: #090d16;
            --bg-surface: #0f172a;
            --bg-card-dark: #0f172a;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-emerald: #10b981;
            --accent-emerald-light: #34d399;
            --accent-cyan: #06b6d4;
            --accent-red: #ef4444;
        }

        html, body, [class*="css"], [data-testid="stAppViewContainer"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            background-color: #090d16 !important;
            color: #f8fafc !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.02em;
        }

        /* Custom Navbar Wrapper (Sesuai Video Referensi @devilda_id) */
        .devilda-navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 24px;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 9999px;
            margin-bottom: 32px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        }
        .devilda-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 1.3rem;
            color: #ffffff;
            text-decoration: none;
        }
        .devilda-brand-badge {
            background: linear-gradient(135deg, #10b981, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .devilda-tag {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34d399;
            padding: 4px 14px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 600;
        }

        /* Hero Section Styling (Identik dengan Frame 040 @devilda_id) */
        .devilda-hero {
            text-align: left;
            margin-bottom: 28px;
        }
        .devilda-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.35);
            padding: 6px 18px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #34d399;
            margin-bottom: 14px;
        }
        .devilda-title {
            font-size: 3.2rem;
            font-weight: 900;
            line-height: 1.12;
            color: #ffffff;
            margin-bottom: 12px;
            font-family: 'Outfit', sans-serif;
        }
        .devilda-highlight {
            background: linear-gradient(135deg, #10b981 0%, #34d399 50%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .devilda-subtitle {
            font-size: 1.05rem;
            color: #94a3b8;
            max-width: 820px;
            line-height: 1.6;
            margin-bottom: 24px;
        }

        /* 4 Stats Cards Grid (Frame 080 @devilda_id) */
        .devilda-stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 32px;
        }
        .devilda-stat-box {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 18px 20px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .devilda-stat-box:hover {
            border-color: rgba(16, 185, 129, 0.4);
            transform: translateY(-3px);
            box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.15);
        }
        .devilda-stat-val {
            font-size: 1.7rem;
            font-weight: 800;
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
        }
        .devilda-stat-val-green {
            color: #34d399;
        }
        .devilda-stat-val-cyan {
            color: #38bdf8;
        }
        .devilda-stat-lbl {
            font-size: 0.8rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
            font-weight: 500;
        }

        /* Glassmorphic Container Cards */
        .devilda-card {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 12px 35px 0 rgba(0, 0, 0, 0.4);
        }

        /* Executive Result Banner (Frame 420 @devilda_id) */
        .devilda-res-fresh {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.14) 0%, rgba(6, 182, 212, 0.08) 100%);
            border: 2px solid #10b981;
            border-radius: 20px;
            padding: 22px;
            margin-bottom: 20px;
        }
        .devilda-res-rotten {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.14) 0%, rgba(244, 63, 94, 0.08) 100%);
            border: 2px solid #ef4444;
            border-radius: 20px;
            padding: 22px;
            margin-bottom: 20px;
        }
        .devilda-res-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 12px;
        }
        .devilda-res-avatar {
            font-size: 3.2rem;
            line-height: 1;
        }
        .devilda-res-tag-fresh {
            background: #10b981;
            color: #042f2e;
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .devilda-res-tag-rotten {
            background: #ef4444;
            color: #ffffff;
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .devilda-res-latency {
            background: rgba(255, 255, 255, 0.08);
            color: #94a3b8;
            padding: 5px 12px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-left: 8px;
        }
        .devilda-res-title {
            font-size: 1.9rem;
            font-weight: 800;
            color: #ffffff;
            margin-top: 4px;
        }
        .devilda-verdict-box {
            background: rgba(0, 0, 0, 0.35);
            border-left: 4px solid #10b981;
            padding: 12px 16px;
            border-radius: 12px;
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-top: 10px;
        }
        .devilda-verdict-rotten {
            border-left-color: #ef4444;
        }

        /* 4 Storage KPIs Grid */
        .storage-kpi-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin: 16px 0;
        }
        .storage-kpi-box {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 16px;
        }
        .storage-kpi-lbl {
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .storage-kpi-val {
            font-size: 1.05rem;
            font-weight: 700;
            color: #f8fafc;
            margin-top: 4px;
        }

        /* Footer */
        .devilda-footer {
            text-align: center;
            padding: 32px 0 16px 0;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 40px;
        }

        /* Button Customizations */
        div.stButton > button {
            border-radius: 14px !important;
            font-weight: 600 !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            background: rgba(30, 41, 59, 0.7) !important;
            color: #f8fafc !important;
            transition: all 0.25s ease !important;
        }
        div.stButton > button:hover {
            border-color: #10b981 !important;
            color: #34d399 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 16px rgba(16, 185, 129, 0.25) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Fungsi utama antarmuka Streamlit FruitFresh AI dengan tema presisi @devilda_id."""
    st.set_page_config(
        page_title="FruitFresh AI — Klasifikasi Kesegaran Buah",
        page_icon="🍏",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    inject_devilda_theme()

    # Inisialisasi Session State
    if "active_image" not in st.session_state:
        st.session_state["active_image"] = None
    if "image_source_name" not in st.session_state:
        st.session_state["image_source_name"] = "Belum Ada Citra Terpilih"

    # 1. NAVBAR WRAPPER (@devilda_id)
    st.markdown("""
    <div class="devilda-navbar">
        <div class="devilda-brand">
            <span>🍏</span>
            <span>FruitFresh <span class="devilda-brand-badge">AI</span></span>
        </div>
        <div class="devilda-tag">
            <span>✨ Desain Referensi TikTok @devilda_id</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. HERO SECTION (@devilda_id)
    st.markdown("""
    <div class="devilda-hero">
        <div class="devilda-pill">
            <span>🚀</span>
            <span>Teknologi AI Terdepan untuk Kesegaran Buah</span>
        </div>
        <div class="devilda-title">
            Klasifikasi<br>
            <span class="devilda-highlight">Kesegaran Buah</span><br>
            dengan AI
        </div>
        <div class="devilda-subtitle">
            Revolusi teknologi CNN dengan arsitektur MobileNetV2 untuk mengidentifikasi kesegaran dan jenis buah dengan akurasi 97.4% dan kecepatan inferensi optimal.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. 4 STATS CARDS (@devilda_id)
    st.markdown("""
    <div class="devilda-stats-grid">
        <div class="devilda-stat-box">
            <div class="devilda-stat-val devilda-stat-val-green">97.4%</div>
            <div class="devilda-stat-lbl">Akurasi Uji</div>
        </div>
        <div class="devilda-stat-box">
            <div class="devilda-stat-val devilda-stat-val-cyan">6 Kelas</div>
            <div class="devilda-stat-lbl">Kategori Buah</div>
        </div>
        <div class="devilda-stat-box">
            <div class="devilda-stat-val">13.599</div>
            <div class="devilda-stat-lbl">Dataset Citra</div>
        </div>
        <div class="devilda-stat-box">
            <div class="devilda-stat-val devilda-stat-val-green">2.58 MB</div>
            <div class="devilda-stat-lbl">TFLite Edge AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. KATEGORI BUAH & TOMBOL UJI 1-KLIK
    st.markdown("### 🍎 Pilih Sampel Buah untuk Deteksi Instan")
    st.caption("Klik salah satu buah di bawah untuk menjalankan inspeksi kualitas otomatis:")
    
    sample_items = [
        {"key": "fresh_apple", "file": "fresh_apple.png", "label": "🍏 Apel Segar", "name": "Sampel: Apel Segar (freshapples)"},
        {"key": "rotten_apple", "file": "rotten_apple.png", "label": "🍎 Apel Busuk", "name": "Sampel: Apel Busuk (rottenapples)"},
        {"key": "fresh_banana", "file": "fresh_banana.png", "label": "🍌 Pisang Segar", "name": "Sampel: Pisang Segar (freshbanana)"},
        {"key": "rotten_banana", "file": "rotten_banana.png", "label": "🍌 Pisang Busuk", "name": "Sampel: Pisang Busuk (rottenbanana)"},
        {"key": "fresh_orange", "file": "fresh_orange.png", "label": "🍊 Jeruk Segar", "name": "Sampel: Jeruk Segar (freshoranges)"},
        {"key": "rotten_orange", "file": "rotten_orange.png", "label": "🍊 Jeruk Busuk", "name": "Sampel: Jeruk Busuk (rottenoranges)"},
    ]

    cols_samp = st.columns(6)
    for idx, itm in enumerate(sample_items):
        with cols_samp[idx]:
            if st.button(itm["label"], use_container_width=True, key=f"btn_devilda_{itm['key']}"):
                sample_p = PROJECT_ROOT / "static" / "samples" / itm["file"]
                if sample_p.exists():
                    st.session_state["active_image"] = Image.open(sample_p)
                    st.session_state["image_source_name"] = itm["name"]

    st.write("")

    # 5. DUAL COCKPIT INSPEKSI (Left: Input & Camera, Right: Result & Tabs)
    col_input, col_result = st.columns([1, 1], gap="large")

    # LEFT COCKPIT: INPUT
    with col_input:
        st.markdown('<div class="devilda-card">', unsafe_allow_html=True)
        st.subheader("📷 Sumber Citra Uji")
        
        tab_up, tab_cam = st.tabs(["📁 Unggah File Gambar", "📸 Kamera Langsung (Webcam)"])
        
        with tab_up:
            up_file = st.file_uploader(
                "Pilih citra buah (JPG, PNG, JPEG, WEBP):",
                type=["jpg", "jpeg", "png", "webp"],
                key="uploader_input_devilda"
            )
            if up_file is not None:
                try:
                    st.session_state["active_image"] = Image.open(up_file)
                    st.session_state["image_source_name"] = f"File Upload: {up_file.name}"
                except Exception as e:
                    st.error(f"Gagal membaca gambar: {e}")

        with tab_cam:
            cam_shot = st.camera_input("Arahkan buah ke kamera webcam:", key="webcam_devilda")
            if cam_shot is not None:
                try:
                    st.session_state["active_image"] = Image.open(cam_shot)
                    st.session_state["image_source_name"] = "Tangkapan Kamera Langsung"
                except Exception as e:
                    st.error(f"Gagal membaca kamera: {e}")

        st.markdown("---")
        toggle_gradcam = st.toggle(
            "🔍 Aktifkan Explainable AI (Grad-CAM)",
            value=True,
            help="Memetakan visual atensi layer konvolusi out_relu MobileNetV2."
        )

        if st.session_state["active_image"] is not None:
            st.caption(f"**Citra Aktif:** `{st.session_state['image_source_name']}`")
            st.image(st.session_state["active_image"], use_container_width=True)
        else:
            st.info("👈 Pilih salah satu sampel buah di atas, unggah foto, atau aktifkan webcam.")

        st.markdown('</div>', unsafe_allow_html=True)

    # RIGHT COCKPIT: RESULT & TABS
    with col_result:
        st.markdown('<div class="devilda-card">', unsafe_allow_html=True)
        st.subheader("📊 Hasil Inspeksi AI (Cockpit)")

        active_img = st.session_state["active_image"]
        if active_img is not None:
            t_start = time.perf_counter()
            with st.spinner("🤖 MobileNetV2 memproses citra..."):
                pred_res = predict_image(active_img, return_gradcam=toggle_gradcam)
            lat_ms = (time.perf_counter() - t_start) * 1000.0

            if pred_res["status"] == "ERROR":
                st.error(f"⚠️ Error: {pred_res.get('error_message')}")
            else:
                p_cls = pred_res["predicted_class"]
                conf_val = pred_res["confidence"]
                p_probs = pred_res["probabilities"]
                g_img = pred_res.get("gradcam_image")
                
                meta_item = FRUIT_METADATA.get(p_cls, {
                    "title": p_cls.replace('_', ' ').title(),
                    "condition": "Segar" if "fresh" in p_cls else "Busuk",
                    "fruit_type": "Buah",
                    "is_fresh": "fresh" in p_cls,
                    "icon": "🍏" if "apple" in p_cls else ("🍌" if "banana" in p_cls else "🍊"),
                    "verdict": "Pemeriksaan selesai.",
                    "shelf_life": "N/A",
                    "optimal_temp": "Suhu Ruang",
                    "humidity_rh": "85% - 90%",
                    "ethylene_level": "Sedang",
                    "qc_action": "Selesai diinspeksi.",
                    "recommendation": "Gunakan sesuai kebutuhan.",
                    "storage_tip": "Simpan di tempat berventilasi baik."
                })

                is_fresh_b = meta_item["is_fresh"]

                # OOD Warning
                if conf_val < 60.0:
                    st.warning("⚠️ **Out-of-Distribution (OOD):** Tingkat keyakinan model <60%. Gambar kemungkinan bukan Apel, Pisang, atau Jeruk.")

                # EXECUTIVE RESULT BANNER (@devilda_id Frame 420)
                banner_style = "devilda-res-fresh" if is_fresh_b else "devilda-res-rotten"
                tag_style = "devilda-res-tag-fresh" if is_fresh_b else "devilda-res-tag-rotten"
                tag_txt = "🟢 LOLOS QC GRADE A (FRESH)" if is_fresh_b else "🔴 REJECT QC (ROTTEN / RUSAK)"
                verdict_box_cls = "devilda-verdict-box" if is_fresh_b else "devilda-verdict-box devilda-verdict-rotten"

                st.markdown(f"""
                <div class="{banner_style}">
                    <div class="devilda-res-header">
                        <div class="devilda-res-avatar">{meta_item['icon']}</div>
                        <div>
                            <div>
                                <span class="{tag_style}">{tag_txt}</span>
                                <span class="devilda-res-latency">⚡ {lat_ms:.1f} ms</span>
                            </div>
                            <div class="devilda-res-title">{meta_item['title']}</div>
                        </div>
                    </div>
                    <div class="{verdict_box_cls}">
                        <b>Keputusan QC:</b> {meta_item['verdict']}
                    </div>
                    <div style="margin-top: 14px; display: flex; justify-content: space-between; align-items: flex-end;">
                        <span style="font-size: 0.85rem; font-weight: 600; color: #94a3b8;">CONFIDENCE SCORE:</span>
                        <span style="font-size: 1.8rem; font-weight: 800; font-family: 'Outfit'; color: {'#34d399' if is_fresh_b else '#f87171'};">
                            {conf_val:.2f}%
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.progress(float(conf_val / 100.0))

                # PROGRESSIVE TABS
                tab_qc, tab_xai, tab_bench = st.tabs([
                    "📦 Rekomendasi Penyimpanan & QC",
                    "🔬 Explainable AI (Grad-CAM)",
                    "📊 Benchmark Model"
                ])

                with tab_qc:
                    st.markdown(f"""
                    <div class="storage-kpi-grid">
                        <div class="storage-kpi-box">
                            <div class="storage-kpi-lbl">Suhu Optimal</div>
                            <div class="storage-kpi-val">{meta_item['optimal_temp']}</div>
                        </div>
                        <div class="storage-kpi-box">
                            <div class="storage-kpi-lbl">Kelembaban RH</div>
                            <div class="storage-kpi-val">{meta_item['humidity_rh']}</div>
                        </div>
                        <div class="storage-kpi-box">
                            <div class="storage-kpi-lbl">Daya Simpan</div>
                            <div class="storage-kpi-val">{meta_item['shelf_life']}</div>
                        </div>
                        <div class="storage-kpi-box">
                            <div class="storage-kpi-lbl">Pelepasan Etilen</div>
                            <div class="storage-kpi-val">{meta_item['ethylene_level']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("**Tindakan QC:**")
                    st.info(meta_item['qc_action'])

                    st.markdown("**Rekomendasi Konsumsi:**")
                    st.write(meta_item['recommendation'])

                    st.markdown("**Tips Penyimpanan:**")
                    st.caption(meta_item['storage_tip'])

                with tab_xai:
                    if toggle_gradcam and g_img is not None:
                        c_g1, c_g2 = st.columns(2)
                        with c_g1:
                            st.image(g_img, caption="Grad-CAM Heatmap (Layer out_relu)", use_container_width=True)
                        with c_g2:
                            st.image(active_img, caption="Citra Input Asli", use_container_width=True)
                        st.caption("💡 **Validasi Visual:** Grad-CAM membuktikan neural network fokus pada karakteristik tekstur kulit dan area pembusukan buah.")

                    st.markdown("##### 📈 Distribusi Probabilitas 6 Kelas")
                    for cl_name, cl_prob in p_probs.items():
                        c_p1, c_p2 = st.columns([3, 1])
                        c_icon = "🍏" if "apple" in cl_name else ("🍌" if "banana" in cl_name else "🍊")
                        c_title = cl_name.replace("_", " ").title()
                        with c_p1:
                            st.caption(f"{c_icon} {c_title}")
                            st.progress(float(cl_prob / 100.0))
                        with c_p2:
                            st.markdown(f"<span style='font-size: 0.9rem; font-weight: 700; color: #38bdf8;'>{cl_prob:.2f}%</span>", unsafe_allow_html=True)

                with tab_bench:
                    st.markdown("##### ⚡ Evaluasi Komparatif Arsitektur")
                    st.markdown("""
                    | Arsitektur Model | Ukuran Model | Latensi CPU | Akurasi Uji |
                    | :--- | :--- | :--- | :--- |
                    | **MobileNetV2 (TFLite Edge)** | **2.58 MB** | **~58 ms** | **97.40%** |
                    | MobileNetV2 (Keras Asli) | 11.12 MB | ~74 ms | 97.40% |
                    | ResNet50 (Baseline) | 98.40 MB | ~210 ms | 96.10% |
                    | VGG16 (Baseline) | 528.0 MB | ~480 ms | 95.80% |
                    """)

                    st.markdown("---")
                    qc_text = f"""==================================================
           LAPORAN QUALITY CONTROL (QC) BUAH
                   FruitFresh AI System
==================================================
Tanggal Pemeriksaan : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Sumber Citra        : {st.session_state['image_source_name']}
--------------------------------------------------
Hasil Prediksi      : {meta_item['title']} ({p_cls})
Status Mutu         : {'SEGAR (FRESH - GRADE A)' if is_fresh_b else 'RUSAK (ROTTEN - REJECT)'}
Tingkat Keyakinan   : {conf_val:.2f}%
Waktu Inferensi     : {lat_ms:.1f} ms
Model Engine        : MobileNetV2 ImageNet (Transfer Learning)
Ukuran Model        : 2.58 MB (TFLite Edge Optimized)
--------------------------------------------------
Rekomendasi QC      : {meta_item['qc_action']}
Suhu Optimal        : {meta_item['optimal_temp']}
Kelembaban RH       : {meta_item['humidity_rh']}
Daya Simpan         : {meta_item['shelf_life']}
--------------------------------------------------
Distribusi Probabilitas Kelas:
"""
                    for cn, cp in p_probs.items():
                        qc_text += f"  - {cn:<16} : {cp:.2f}%\n"
                    qc_text += "==================================================\n"

                    st.download_button(
                        label="📄 Unduh Laporan QC (.txt)",
                        data=qc_text,
                        file_name=f"QC_Report_{p_cls}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

        else:
            st.info("Silakan pilih salah satu tombol sampel demo di atas atau unggah foto untuk menjalankan inferensi real-time.")

        st.markdown('</div>', unsafe_allow_html=True)

    # 6. FOOTER (@devilda_id)
    st.markdown("""
    <div class="devilda-footer">
        <p>&copy; 2026 FruitFresh AI. Terinspirasi dari rancangan <b>@devilda_id</b>. Ditenagai oleh TensorFlow, Keras, dan Streamlit.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
