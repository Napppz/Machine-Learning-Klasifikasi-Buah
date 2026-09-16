"""
🍎 FruitFresh AI: Enterprise Fruit Quality & Freshness Inspection
Deep Learning MobileNetV2 • Explainable AI (Grad-CAM) • Real-Time QC Protocol
Desain Antarmuka Ultra-Modern Terinspirasi dari Referensi TikTok @devilda_id
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
# 1. Metadata Komprehensif Cold Chain & QC Protocol Buah
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

def load_custom_css():
    """Menyuntikkan CSS Modern Glassmorphism & Dark Theme ala TikTok @devilda_id."""
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        /* Global Reset & Typography */
        html, body, [class*="css"], [data-testid="stAppViewContainer"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #0b0f19 !important;
            color: #f8fafc !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.02em;
        }

        /* Ambient Glow & Floating Animation */
        @keyframes float-badge {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        @keyframes pulse-emerald {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            70% { box-shadow: 0 0 0 16px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        @keyframes pulse-crimson {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
            70% { box-shadow: 0 0 0 16px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }

        /* Glassmorphism Card Container */
        .cyber-card {
            background: rgba(17, 24, 39, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 12px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Hero Header Styling */
        .hero-pill-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.2));
            border: 1px solid rgba(16, 185, 129, 0.35);
            padding: 6px 16px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #34d399;
            margin-bottom: 12px;
            animation: float-badge 3s ease-in-out infinite;
        }

        .hero-title-gradient {
            font-size: 2.8rem;
            font-weight: 900;
            background: linear-gradient(135deg, #ffffff 0%, #10b981 50%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.15;
            margin-bottom: 8px;
        }

        .hero-subtitle-text {
            color: #94a3b8;
            font-size: 1.05rem;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        /* Stat Grid Pill Cards */
        .stat-grid-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 24px;
        }
        .stat-pill {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 14px 16px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .stat-pill:hover {
            border-color: rgba(16, 185, 129, 0.4);
            transform: translateY(-2px);
        }
        .stat-val {
            font-size: 1.4rem;
            font-weight: 800;
            color: #38bdf8;
            font-family: 'Outfit', sans-serif;
        }
        .stat-lbl {
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }

        /* Executive Result Card Banner */
        .exec-banner-fresh {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%);
            border: 2px solid #10b981;
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 20px;
            animation: pulse-emerald 3s infinite;
        }
        .exec-banner-rotten {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(244, 63, 94, 0.08) 100%);
            border: 2px solid #ef4444;
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 20px;
            animation: pulse-crimson 3s infinite;
        }

        .exec-header-flex {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 12px;
        }
        .exec-avatar {
            font-size: 3rem;
            line-height: 1;
            filter: drop-shadow(0 4px 10px rgba(0,0,0,0.4));
        }
        .exec-badge-fresh {
            background: #10b981;
            color: #042f2e;
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            display: inline-block;
        }
        .exec-badge-rotten {
            background: #ef4444;
            color: #ffffff;
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            display: inline-block;
        }
        .exec-latency-badge {
            background: rgba(255, 255, 255, 0.08);
            color: #94a3b8;
            padding: 5px 12px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-block;
            margin-left: 8px;
        }
        .exec-title {
            font-size: 1.8rem;
            font-weight: 800;
            color: #ffffff;
            margin-top: 4px;
        }
        .exec-verdict {
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-top: 8px;
            padding: 12px 16px;
            background: rgba(0, 0, 0, 0.25);
            border-radius: 12px;
            border-left: 4px solid #10b981;
        }
        .exec-verdict-rotten {
            border-left-color: #ef4444;
        }

        /* Metric KPI 4-grid in Storage Tab */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin: 16px 0;
        }
        .kpi-box {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 16px;
        }
        .kpi-box-icon {
            font-size: 1.2rem;
            margin-bottom: 4px;
        }
        .kpi-box-val {
            font-size: 1.05rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .kpi-box-lbl {
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Out-of-Distribution Warning */
        .ood-warning-card {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.1));
            border: 1px solid #f59e0b;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 16px;
            color: #fbbf24;
        }

        /* Button Enhancements */
        div.stButton > button {
            border-radius: 12px !important;
            font-weight: 600 !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            background: rgba(30, 41, 59, 0.8) !important;
            color: #f8fafc !important;
            transition: all 0.25s ease !important;
        }
        div.stButton > button:hover {
            border-color: #10b981 !important;
            color: #34d399 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2) !important;
        }

        /* Sidebar Beautification */
        [data-testid="stSidebar"] {
            background-color: #070b14 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render Sidebar informasi model & panduan."""
    with st.sidebar:
        st.markdown("### 🍏 FruitFresh AI Engine")
        st.caption("Deep Learning Quality Inspection System")
        st.image("https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400&auto=format&fit=crop&q=80", use_container_width=True)
        
        st.markdown("""
        Sistem Computer Vision industri untuk **inspeksi otomatis kualitas dan kesegaran buah** di sektor ritel & pascapanen modern.
        """)
        st.divider()

        st.markdown("#### 🏆 Performa Model Terverifikasi")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Test Accuracy", "97.40%", delta="Verified")
        with c2:
            st.metric("Macro F1", "97.43%", delta="Optimal")

        st.markdown("""
        - **Arsitektur:** MobileNetV2 ImageNet
        - **Dataset:** 13.599 Citra Uji & Latih
        - **Explainable AI:** Grad-CAM Active
        - **Format:** TFLite Edge & Keras Native
        """)
        st.divider()

        st.markdown("#### 📱 Optimasi Edge & Kompresi")
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.08); padding: 14px; border-radius: 12px; font-size: 0.85rem; color: #cbd5e1;">
            • Model Asli Keras: <b>11.12 MB</b><br>
            • Model TFLite Edge: <b>2.58 MB</b><br>
            • Rasio Kompresi: <b style="color: #34d399;">76.8% Lebih Ringan</b><br>
            • Rata-rata Latensi: <b>~58 ms (CPU)</b>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        with st.expander("🎓 Tips Presentasi Sidang Kuliah"):
            st.markdown("""
            1. **Sorot Transfer Learning**: Menggunakan fitur ekstraksi ImageNet untuk efisiensi pelatihan 13.599 citra.
            2. **Demonstrasikan Grad-CAM**: Buktikan model fokus pada tekstur kulit & titik pembusukan, bukan background foto.
            3. **Tunjukkan Kompresi TFLite**: Model 2.58 MB membuktikan kesiapan deployment pada perangkat IoT/Raspberry Pi atau Android.
            """)

def main():
    """Fungsi utama antarmuka Streamlit FruitFresh AI."""
    # Konfigurasi Halaman Streamlit
    st.set_page_config(
        page_title="FruitFresh AI — Smart Fruit Inspection",
        page_icon="🍏",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_custom_css()
    render_sidebar()

    # Inisialisasi Session State
    if "active_image" not in st.session_state:
        st.session_state["active_image"] = None
    if "image_source_name" not in st.session_state:
        st.session_state["image_source_name"] = "Belum Ada Citra Terpilih"

    # HERO HEADER SECTION
    st.markdown("""
    <div>
        <div class="hero-pill-badge">
            <span>✨ Enterprise Computer Vision</span>
            <span>•</span>
            <span>MobileNetV2 Transfer Learning</span>
            <span>•</span>
            <span>Grad-CAM XAI</span>
        </div>
        <div class="hero-title-gradient">🍎 FruitFresh AI</div>
        <div class="hero-subtitle-text">
            Sistem klasifikasi otomatis kualitas dan kesegaran buah berbasis Deep Learning dengan akurasi terverifikasi 97.40% pada data uji independen.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 STATS PILLS
    st.markdown("""
    <div class="stat-grid-row">
        <div class="stat-pill">
            <div class="stat-val">97.40%</div>
            <div class="stat-lbl">Akurasi Uji</div>
        </div>
        <div class="stat-pill">
            <div class="stat-val">6 Kelas</div>
            <div class="stat-lbl">Apel, Pisang, Jeruk</div>
        </div>
        <div class="stat-pill">
            <div class="stat-val">13.599</div>
            <div class="stat-lbl">Citra Dataset</div>
        </div>
        <div class="stat-pill">
            <div class="stat-val">2.58 MB</div>
            <div class="stat-lbl">TFLite Edge AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # SAMPLE BUTTON BAR (1-Click Demo)
    st.markdown("##### 🧪 Coba Langsung dengan Sampel Demo 1-Klik:")
    sample_files = {
        "fresh_apple": {"path": PROJECT_ROOT / "static" / "samples" / "fresh_apple.png", "label": "🍏 Apel Segar", "name": "Sampel: Apel Segar (freshapples)"},
        "rotten_apple": {"path": PROJECT_ROOT / "static" / "samples" / "rotten_apple.png", "label": "🍎 Apel Busuk", "name": "Sampel: Apel Busuk (rottenapples)"},
        "fresh_banana": {"path": PROJECT_ROOT / "static" / "samples" / "fresh_banana.png", "label": "🍌 Pisang Segar", "name": "Sampel: Pisang Segar (freshbanana)"},
        "rotten_banana": {"path": PROJECT_ROOT / "static" / "samples" / "rotten_banana.png", "label": "🍌 Pisang Busuk", "name": "Sampel: Pisang Busuk (rottenbanana)"},
        "fresh_orange": {"path": PROJECT_ROOT / "static" / "samples" / "fresh_orange.png", "label": "🍊 Jeruk Segar", "name": "Sampel: Jeruk Segar (freshoranges)"},
        "rotten_orange": {"path": PROJECT_ROOT / "static" / "samples" / "rotten_orange.png", "label": "🍊 Jeruk Busuk", "name": "Sampel: Jeruk Busuk (rottenoranges)"},
    }

    cols = st.columns(6)
    for idx, (k, v) in enumerate(sample_files.items()):
        with cols[idx]:
            if st.button(v["label"], use_container_width=True, key=f"btn_sample_{k}"):
                if v["path"].exists():
                    st.session_state["active_image"] = Image.open(v["path"])
                    st.session_state["image_source_name"] = v["name"]
                else:
                    st.warning(f"File sampel {v['path'].name} tidak ditemukan.")

    st.write("")

    # MAIN DUAL-COLUMN COCKPIT
    col_left, col_right = st.columns([1, 1], gap="large")

    # LEFT COLUMN: INPUT SOURCE
    with col_left:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.subheader("📷 Sumber Citra Uji")
        
        tab_up, tab_cam = st.tabs(["📁 Unggah File Gambar", "📸 Kamera Langsung (Webcam)"])
        
        with tab_up:
            uploaded = st.file_uploader(
                "Pilih file citra buah (JPG, PNG, JPEG, WEBP):",
                type=["jpg", "jpeg", "png", "webp"],
                key="uploader_input"
            )
            if uploaded is not None:
                try:
                    st.session_state["active_image"] = Image.open(uploaded)
                    st.session_state["image_source_name"] = f"File Upload: {uploaded.name}"
                except Exception as e:
                    st.error(f"Gagal memproses gambar: {e}")

        with tab_cam:
            camera_img = st.camera_input("Arahkan buah ke lensa kamera webcam:", key="webcam_input")
            if camera_img is not None:
                try:
                    st.session_state["active_image"] = Image.open(camera_img)
                    st.session_state["image_source_name"] = "Tangkapan Kamera Langsung (Webcam)"
                except Exception as e:
                    st.error(f"Gagal membaca input kamera: {e}")

        st.markdown("---")
        enable_xai = st.toggle(
            "🔍 Aktifkan Explainable AI (Grad-CAM Heatmap)",
            value=True,
            help="Memetakan layer konvolusi out_relu untuk memvalidasi area piksel penentu klasifikasi."
        )

        # Image Preview
        if st.session_state["active_image"] is not None:
            st.caption(f"**Citra Aktif:** `{st.session_state['image_source_name']}`")
            st.image(st.session_state["active_image"], use_container_width=True)
        else:
            st.info("👈 Silakan pilih tombol sampel buah di atas, unggah foto, atau aktifkan kamera.")

        st.markdown('</div>', unsafe_allow_html=True)

    # RIGHT COLUMN: INFERENCE & RESULTS
    with col_right:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.subheader("📊 Hasil Inspeksi AI (Cockpit)")

        active_img = st.session_state["active_image"]
        if active_img is not None:
            t0 = time.perf_counter()
            with st.spinner("🤖 MobileNetV2 menganalisis karakteristik visual citra..."):
                res = predict_image(active_img, return_gradcam=enable_xai)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0

            if res["status"] == "ERROR":
                st.error(f"⚠️ **Error Analisis:** {res.get('error_message')}")
            else:
                pred_cls = res["predicted_class"]
                conf = res["confidence"]
                probs = res["probabilities"]
                gradcam_img = res.get("gradcam_image")
                
                meta = FRUIT_METADATA.get(pred_cls, {
                    "title": pred_cls.replace('_', ' ').title(),
                    "condition": "Segar" if "fresh" in pred_cls else "Busuk",
                    "fruit_type": "Buah",
                    "is_fresh": "fresh" in pred_cls,
                    "icon": "🍏" if "apple" in pred_cls else ("🍌" if "banana" in pred_cls else "🍊"),
                    "verdict": "Pemeriksaan selesai.",
                    "shelf_life": "N/A",
                    "optimal_temp": "Suhu Ruang",
                    "humidity_rh": "85% - 90%",
                    "ethylene_level": "Sedang",
                    "qc_action": "Selesai diinspeksi.",
                    "aroma_texture": "Standar",
                    "recommendation": "Gunakan sesuai kebutuhan.",
                    "storage_tip": "Simpan di tempat berventilasi baik."
                })

                is_fresh = meta["is_fresh"]
                is_ood = conf < 60.0

                # OOD Rejection Warning
                if is_ood:
                    st.markdown("""
                    <div class="ood-warning-card">
                        <b>⚠️ Peringatan Out-of-Distribution (OOD):</b><br>
                        Tingkat keyakinan model di bawah ambang batas batas aman (60.0%). 
                        Citra kemungkinan bukan salah satu dari 3 buah target (Apel, Pisang, Jeruk) atau resolusi foto terlalu buram.
                    </div>
                    """, unsafe_allow_html=True)

                # EXECUTIVE RESULT BANNER
                banner_cls = "exec-banner-fresh" if is_fresh else "exec-banner-rotten"
                badge_cls = "exec-badge-fresh" if is_fresh else "exec-badge-rotten"
                verdict_cls = "exec-verdict" if is_fresh else "exec-verdict exec-verdict-rotten"
                status_label = "🟢 LOLOS QC GRADE A (FRESH)" if is_fresh else "🔴 REJECT QC (ROTTEN / RUSAK)"

                st.markdown(f"""
                <div class="{banner_cls}">
                    <div class="exec-header-flex">
                        <div class="exec-avatar">{meta['icon']}</div>
                        <div>
                            <div>
                                <span class="{badge_cls}">{status_label}</span>
                                <span class="exec-latency-badge">⚡ {elapsed_ms:.1f} ms</span>
                            </div>
                            <div class="exec-title">{meta['title']}</div>
                        </div>
                    </div>
                    <div class="{verdict_cls}">
                        <b>Keputusan QC:</b> {meta['verdict']}
                    </div>
                    <div style="margin-top: 14px; display: flex; justify-content: space-between; align-items: flex-end;">
                        <span style="font-size: 0.85rem; font-weight: 600; color: #94a3b8;">CONFIDENCE SCORE:</span>
                        <span style="font-size: 1.8rem; font-weight: 800; font-family: 'Outfit'; color: {'#34d399' if is_fresh else '#f87171'};">
                            {conf:.2f}%
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.progress(float(conf / 100.0))

                # PROGRESSIVE TABS
                res_tab1, res_tab2, res_tab3 = st.tabs([
                    "📦 Rekomendasi Penyimpanan & QC",
                    "🔬 Explainable AI & Grad-CAM",
                    "📊 Benchmark Model"
                ])

                # TAB 1: COLD CHAIN & QC PROTOCOL
                with res_tab1:
                    st.markdown(f"""
                    <div class="kpi-grid">
                        <div class="kpi-box">
                            <div class="kpi-box-icon">🌡️</div>
                            <div class="kpi-box-lbl">Suhu Optimal</div>
                            <div class="kpi-box-val">{meta['optimal_temp']}</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-box-icon">💧</div>
                            <div class="kpi-box-lbl">Kelembaban RH</div>
                            <div class="kpi-box-val">{meta['humidity_rh']}</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-box-icon">⏳</div>
                            <div class="kpi-box-lbl">Daya Simpan</div>
                            <div class="kpi-box-val">{meta['shelf_life']}</div>
                        </div>
                        <div class="kpi-box">
                            <div class="kpi-box-icon">💨</div>
                            <div class="kpi-box-lbl">Sensitivitas Etilen</div>
                            <div class="kpi-box-val">{meta['ethylene_level']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"**Tindakan Operasional QC:**")
                    st.info(meta['qc_action'])

                    st.markdown(f"**Rekomendasi Konsumsi & Keamanan:**")
                    st.write(meta['recommendation'])

                    st.markdown(f"**Tips Penyimpanan Komersial:**")
                    st.caption(meta['storage_tip'])

                # TAB 2: EXPLAINABLE AI & PROBABILITIES
                with res_tab2:
                    if enable_xai and gradcam_img is not None:
                        cam_col1, cam_col2 = st.columns(2)
                        with cam_col1:
                            st.image(gradcam_img, caption="Grad-CAM Heatmap (Fokus Atensi Layer out_relu)", use_container_width=True)
                        with cam_col2:
                            st.image(active_img, caption="Citra Input Asli", use_container_width=True)

                        st.caption("💡 **Validasi Visual Ilmiah**: Grad-CAM membuktikan neural network MobileNetV2 mengarahkan bobot atensinya pada bercak pembusukan dan tekstur kulit spesifik buah.")

                    st.markdown("##### 📈 Distribusi Probabilitas 6 Kelas")
                    for cls_name, p in probs.items():
                        c_p1, c_p2 = st.columns([3, 1])
                        c_emoji = "🍏" if "apple" in cls_name else ("🍌" if "banana" in cls_name else "🍊")
                        c_clean = cls_name.replace("_", " ").title()
                        with c_p1:
                            st.caption(f"{c_emoji} {c_clean}")
                            st.progress(float(p / 100.0))
                        with c_p2:
                            st.markdown(f"<span style='font-size: 0.9rem; font-weight: 700; color: #38bdf8;'>{p:.2f}%</span>", unsafe_allow_html=True)

                # TAB 3: BENCHMARK & ARCHITECTURE
                with res_tab3:
                    st.markdown("##### ⚡ Evaluasi Komparatif Arsitektur CNN")
                    st.markdown("""
                    | Model Arsitektur | Ukuran Model | Latensi CPU | Akurasi Uji |
                    | :--- | :--- | :--- | :--- |
                    | **MobileNetV2 (TFLite Edge)** | **2.58 MB** | **~58 ms** | **97.40%** |
                    | MobileNetV2 (Keras Asli) | 11.12 MB | ~74 ms | 97.40% |
                    | ResNet50 (Baseline) | 98.40 MB | ~210 ms | 96.10% |
                    | VGG16 (Baseline) | 528.0 MB | ~480 ms | 95.80% |
                    """)

                    st.markdown("---")
                    # Export QC Report Download
                    report_text = f"""==================================================
           LAPORAN QUALITY CONTROL (QC) BUAH
                   FruitFresh AI System
==================================================
Tanggal Pemeriksaan : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Sumber Citra        : {st.session_state['image_source_name']}
--------------------------------------------------
Hasil Prediksi      : {meta['title']} ({pred_cls})
Status Mutu         : {'SEGAR (FRESH - GRADE A)' if is_fresh else 'RUSAK (ROTTEN - REJECT)'}
Tingkat Keyakinan   : {conf:.2f}%
Waktu Inferensi     : {elapsed_ms:.1f} ms
Model Engine        : MobileNetV2 ImageNet (Transfer Learning)
Ukuran Model        : 2.58 MB (TFLite Edge Optimized)
--------------------------------------------------
Rekomendasi QC      : {meta['qc_action']}
Suhu Optimal        : {meta['optimal_temp']}
Kelembaban RH       : {meta['humidity_rh']}
Daya Simpan         : {meta['shelf_life']}
--------------------------------------------------
Distribusi Probabilitas Kelas:
"""
                    for c_name, c_prob in probs.items():
                        report_text += f"  - {c_name:<16} : {c_prob:.2f}%\n"
                    report_text += "==================================================\n"

                    st.download_button(
                        label="📄 Unduh Laporan QC (.txt)",
                        data=report_text,
                        file_name=f"QC_Report_{pred_cls}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

        else:
            st.info("Menunggu input citra... Silakan pilih salah satu tombol sampel demo di atas atau unggah foto untuk menjalankan inferensi real-time.")
            
            st.markdown("#### 🍏 Kategori Buah yang Didukung:")
            c_sup1, c_sup2 = st.columns(2)
            with c_sup1:
                st.markdown("- 🍏 **Fresh Apple** *(Apel Segar)*")
                st.markdown("- 🍌 **Fresh Banana** *(Pisang Segar)*")
                st.markdown("- 🍊 **Fresh Orange** *(Jeruk Segar)*")
            with c_sup2:
                st.markdown("- 🍎 **Rotten Apple** *(Apel Busuk)*")
                st.markdown("- 🍌 **Rotten Banana** *(Pisang Busuk)*")
                st.markdown("- 🍊 **Rotten Orange** *(Jeruk Busuk)*")

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
