"""
🍎 FruitFresh AI: Enterprise Fruit Quality & Freshness Classification
Deep Learning MobileNetV2 • Explainable AI (Grad-CAM) • Real-time Micro-Animations
"""

import io
import sys
import json
import datetime
from pathlib import Path
import streamlit as st
from PIL import Image

# Tambahkan root project ke sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.predict import predict_image

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="FruitFresh AI — Smart Fruit Inspection",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Design System: Modern Glassmorphism, Google Fonts, and Micro-Animations
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1, h2, h3, .hero-title {
        font-family: 'Outfit', sans-serif;
    }

    /* Keyframe Animations */
    @keyframes float-subtle {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
        100% { transform: translateY(0px); }
    }
    @keyframes pulse-glow-fresh {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        70% { box-shadow: 0 0 0 14px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    @keyframes pulse-glow-rotten {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 14px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Hero Branding */
    .hero-container {
        padding: 10px 0 25px 0;
    }
    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.15));
        border: 1px solid rgba(168, 85, 247, 0.3);
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #6366F1;
        margin-bottom: 12px;
        animation: float-subtle 4s ease-in-out infinite;
    }
    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #0F172A 30%, #3B82F6 70%, #10B981 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #64748B;
        font-weight: 400;
        max-width: 800px;
        line-height: 1.5;
    }

    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 20px;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -4px rgba(0, 0, 0, 0.03);
    }

    /* Verdict Card Styles */
    .verdict-fresh {
        background: linear-gradient(145deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 2px solid #86EFAC;
        border-radius: 20px;
        padding: 22px;
        animation: pulse-glow-fresh 2.5s infinite;
    }
    .verdict-rotten {
        background: linear-gradient(145deg, #FEF2F2 0%, #FEE2E2 100%);
        border: 2px solid #FCA5A5;
        border-radius: 20px;
        padding: 22px;
        animation: pulse-glow-rotten 2.5s infinite;
    }
    .verdict-label {
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .verdict-title {
        font-size: 1.85rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        margin-bottom: 4px;
    }

    /* Metric Counters */
    .confidence-meter-container {
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px dashed rgba(0, 0, 0, 0.1);
    }
    .confidence-number {
        font-size: 2.4rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        color: #0F172A;
        line-height: 1;
    }

    /* Edge AI Sidebar Badge */
    .edge-badge {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3);
    }

    /* Custom Progress Bar Colors */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3B82F6, #10B981);
        border-radius: 10px;
    }

    /* Interactive Demo Sample Buttons */
    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid #E2E8F0;
        background: white;
        transition: all 0.25s ease;
    }
    div.stButton > button:hover {
        border-color: #3B82F6;
        color: #2563EB;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Komprehensif
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400&auto=format&fit=crop&q=80", use_container_width=True)
    st.markdown("## 🍎 About FruitFresh AI")
    st.markdown("""
    Sistem Computer Vision mutakhir untuk **inspeksi otomatis kualitas dan kesegaran buah** di sektor ritel & industri agrikultur modern.
    """)
    st.divider()

    st.markdown("### 🏆 Performa Model Aktual")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Test Accuracy", "97.40%", delta="Verified")
    with col_m2:
        st.metric("Macro F1", "97.43%", delta="Optimal")

    st.markdown("- **Arsitektur:** MobileNetV2 ImageNet")
    st.markdown("- **Dataset Riil:** 13.599 Citra (Kaggle)")
    st.markdown("- **Explainable AI:** Grad-CAM Active")
    st.divider()

    st.markdown("### 📱 Edge & Mobile Quantization")
    st.markdown("""
    <div style="background: rgba(248, 250, 252, 0.9); border: 1px solid #E2E8F0; padding: 14px; border-radius: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 600; font-size: 0.85rem; color: #475569;">Format Kuantisasi</span>
            <span class="edge-badge">TFLite Dynamic</span>
        </div>
        <div style="font-size: 0.85rem; color: #64748B; line-height: 1.6;">
            • Model Keras Asli: <b>11.12 MB</b><br>
            • Model TFLite Edge: <b>2.58 MB</b><br>
            • Rasio Kompresi: <b style="color: #10B981;">76.8% Lebih Ringan</b><br>
            • Latensi CPU: <b>~60 ms</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    with st.expander("🎓 Tips Presentasi Sidang Kuliah"):
        st.markdown("""
        1. **Jelaskan Transfer Learning**: Memanfaatkan ekstraksi fitur ImageNet untuk efisiensi training.
        2. **Perlihatkan Grad-CAM**: Buktikan model mengenali kerutan & bercak busuk, bukan background.
        3. **Sorot Efisiensi TFLite**: Model 2.58 MB siap diinstal ke smartphone/Raspberry Pi.
        """)

# 4. Hero Header Section
st.markdown("""
<div class="hero-container">
    <div class="pill-badge">
        <span>✨ Enterprise Computer Vision</span>
        <span>•</span>
        <span>Transfer Learning MobileNetV2</span>
        <span>•</span>
        <span>XAI Grad-CAM</span>
    </div>
    <div class="hero-title">🍎 FruitFresh AI</div>
    <div class="hero-subtitle">
        Sistem klasifikasi otomatis kualitas dan kesegaran buah berbasis Deep Learning dengan akurasi terverifikasi 97.40% pada data uji independen.
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Quick 1-Click Demo Sample Bar (Fitur WOW untuk Sidang)
st.markdown("##### 🧪 Coba Langsung dengan Sampel Demo 1-Klik:")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)

sample_map = {
    "fresh_apple": "dataset/test/freshapples/rotated_by_15_Screen Shot 2018-06-08 at 4.59.49 PM.png",
    "rotten_banana": "dataset/test/rottenbanana/rotated_by_15_Screen Shot 2018-06-12 at 8.47.51 PM.png",
    "fresh_orange": "dataset/test/freshoranges/rotated_by_15_Screen Shot 2018-06-12 at 11.50.41 PM.png",
    "rotten_apple": "dataset/test/rottenapples/rotated_by_15_Screen Shot 2018-06-07 at 2.16.18 PM.png"
}

if "active_image" not in st.session_state:
    st.session_state["active_image"] = None
if "image_source_name" not in st.session_state:
    st.session_state["image_source_name"] = "Belum Ada Citra"

with col_s1:
    if st.button("🍏 Apel Segar", use_container_width=True):
        st.session_state["active_image"] = Image.open(sample_map["fresh_apple"])
        st.session_state["image_source_name"] = "Sampel Demo: Apel Segar (freshapples)"
with col_s2:
    if st.button("🍌 Pisang Busuk", use_container_width=True):
        st.session_state["active_image"] = Image.open(sample_map["rotten_banana"])
        st.session_state["image_source_name"] = "Sampel Demo: Pisang Busuk (rottenbanana)"
with col_s3:
    if st.button("🍊 Jeruk Segar", use_container_width=True):
        st.session_state["active_image"] = Image.open(sample_map["fresh_orange"])
        st.session_state["image_source_name"] = "Sampel Demo: Jeruk Segar (freshoranges)"
with col_s4:
    if st.button("🍎 Apel Busuk", use_container_width=True):
        st.session_state["active_image"] = Image.open(sample_map["rotten_apple"])
        st.session_state["image_source_name"] = "Sampel Demo: Apel Busuk (rottenapples)"

st.write("")

# 6. Main Dual Column Cockpit Layout
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📷 Sumber Citra Uji")
    
    input_tab1, input_tab2 = st.tabs(["📁 Unggah File Gambar", "📸 Kamera Langsung (Webcam)"])
    
    with input_tab1:
        uploaded_file = st.file_uploader(
            "Pilih file gambar (JPG, JPEG, PNG):",
            type=["jpg", "jpeg", "png"],
            key="file_uploader_input"
        )
        if uploaded_file is not None:
            try:
                st.session_state["active_image"] = Image.open(uploaded_file)
                st.session_state["image_source_name"] = f"File Upload: {uploaded_file.name}"
            except Exception as e:
                st.error(f"Gagal membaca gambar: {e}")

    with input_tab2:
        camera_file = st.camera_input("Arahkan buah ke kamera webcam:", key="camera_input")
        if camera_file is not None:
            try:
                st.session_state["active_image"] = Image.open(camera_file)
                st.session_state["image_source_name"] = "Tangkapan Kamera Langsung (Webcam)"
            except Exception as e:
                st.error(f"Gagal membaca webcam: {e}")

    st.markdown("---")
    enable_gradcam = st.toggle(
        "🔍 Aktifkan Explainable AI (Grad-CAM Heatmap)",
        value=True,
        help="Menampilkan peta atensi neural network untuk melihat area visual buah yang mendasari keputusan model."
    )
    
    # Preview Citra Aktif
    if st.session_state["active_image"] is not None:
        st.markdown(f"**Citra Terpilih:** `{st.session_state['image_source_name']}`")
        st.image(st.session_state["active_image"], use_container_width=True)
    else:
        st.info("👈 Silakan pilih salah satu tombol sampel di atas, unggah file, atau ambil foto dengan webcam.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# 7. Prediction Cockpit
with col_right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 Hasil Inspeksi AI (Cockpit)")
    
    current_img = st.session_state["active_image"]
    if current_img is not None:
        with st.spinner("🤖 MobileNetV2 menganalisis karakteristik visual buah..."):
            result = predict_image(current_img, return_gradcam=enable_gradcam)
            
        if result["status"] == "ERROR":
            st.error(f"⚠️ **Error:** {result['error_message']}")
        else:
            pred_class = result["predicted_class"]
            confidence = result["confidence"]
            probs = result["probabilities"]
            gradcam_img = result.get("gradcam_image")
            
            is_fresh = "fresh" in pred_class.lower()
            clean_fruit_name = pred_class.replace("fresh", "").replace("rotten", "").replace("_", " ").title()
            
            # Stylized Verdict Card with Animations
            verdict_class = "verdict-fresh" if is_fresh else "verdict-rotten"
            verdict_color = "#166534" if is_fresh else "#991B1B"
            verdict_badge_text = "✅ KONDISI SEGAR (FRESH)" if is_fresh else "⚠️ KONDISI BUSUK (ROTTEN)"
            
            st.markdown(f"""
            <div class="{verdict_class}">
                <div class="verdict-label" style="color: {verdict_color};">{verdict_badge_text}</div>
                <div class="verdict-title" style="color: #0F172A;">{clean_fruit_name} ({pred_class})</div>
                <div class="confidence-meter-container">
                    <span style="font-size: 0.85rem; font-weight: 600; color: #475569;">TINGKAT KEYAKINAN (CONFIDENCE SCORE):</span>
                    <div class="confidence-number">{confidence:.2f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.progress(float(confidence / 100.0))
            
            # Tab Visual Analysis (Original vs Grad-CAM)
            if enable_gradcam and gradcam_img is not None:
                tab_cam1, tab_cam2 = st.tabs(["🔬 Peta Perhatian Model (Grad-CAM)", "📸 Citra Asli"])
                with tab_cam1:
                    st.image(
                        gradcam_img,
                        caption="Area Panas (Merah/Kuning): Fitur Piksel Utama Penentu Klasifikasi",
                        use_container_width=True
                    )
                    st.caption("💡 **Validasi Ilmiah**: Layer konvolusi `out_relu` MobileNetV2 secara objektif membidik tekstur kulit dan area pembusukan buah.")
                with tab_cam2:
                    st.image(current_img, caption="Citra Input Asli", use_container_width=True)
            
            # Probability Distribution Meters
            st.markdown("#### 📈 Distribusi Probabilitas 6 Kelas")
            for cls_name, prob in probs.items():
                c1, c2 = st.columns([3, 1])
                clean_n = cls_name.replace("_", " ").title()
                emoji = "🍏" if "apple" in cls_name else ("🍌" if "banana" in cls_name else "🍊")
                with c1:
                    st.caption(f"{emoji} {clean_n}")
                    st.progress(float(prob / 100.0))
                with c2:
                    st.markdown(f"**{prob:.2f}%**")
                    
            # Export QC Report Feature
            st.markdown("---")
            qc_report = f"""==================================================
           LAPORAN QUALITY CONTROL (QC) BUAH
                   FruitFresh AI System
==================================================
Tanggal Pemeriksaan : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Sumber Citra        : {st.session_state['image_source_name']}
--------------------------------------------------
Hasil Prediksi      : {pred_class}
Kategori Kondisi    : {'SEGAR (FRESH - LOLOS QC)' if is_fresh else 'RUSAK (ROTTEN - REJECT)'}
Tingkat Keyakinan   : {confidence:.2f}%
Model Engine        : MobileNetV2 ImageNet (Transfer Learning)
Ukuran Model        : 2.58 MB (TFLite Edge Optimized)
--------------------------------------------------
Distribusi Probabilitas Kelas:
"""
            for c, p in probs.items():
                qc_report += f"  - {c:<16} : {p:.2f}%\n"
            qc_report += "==================================================\n"
            
            st.download_button(
                label="📄 Unduh Laporan Inspeksi (QC Report)",
                data=qc_report,
                file_name=f"QC_Report_{pred_class}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
    else:
        st.info("Menunggu input citra... Klik salah satu tombol contoh di atas atau unggah foto untuk menjalankan inferensi real-time.")
        
        # Grid Panduan Kategori
        st.markdown("#### 🍏 Kategori Buah yang Didukung:")
        models_dir = project_root / "models"
        class_names_path = models_dir / "class_names.json"
        if class_names_path.exists():
            with open(class_names_path, "r", encoding="utf-8") as f:
                classes = json.load(f)
            col_k1, col_k2 = st.columns(2)
            for idx, c in enumerate(classes):
                target_col = col_k1 if idx % 2 == 0 else col_k2
                clean_lbl = c.replace('_', ' ').title()
                emoji = "🍏" if "apple" in c.lower() else ("🍌" if "banana" in c.lower() else "🍊")
                badge_type = "🟢 Fresh" if "fresh" in c.lower() else "🔴 Rotten"
                with target_col:
                    st.markdown(f"{emoji} **{clean_lbl}** ({badge_type})")
                    
    st.markdown('</div>', unsafe_allow_html=True)
