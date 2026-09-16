---
title: FruitFresh AI
emoji: 🍏
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# 🍎 FruitFresh AI: Klasifikasi Kualitas & Kesegaran Buah Menggunakan Deep Learning

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16%2B-orange.svg)](https://www.tensorflow.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Test Accuracy](https://img.shields.io/badge/Test%20Accuracy-97.40%25-brightgreen.svg)]()
[![F1 Score](https://img.shields.io/badge/Macro%20F1--Score-97.43%25-success.svg)]()

Aplikasi Computer Vision berbasis Deep Learning dengan arsitektur **Transfer Learning MobileNetV2** untuk mengklasifikasikan kondisi buah menjadi **Fresh (Segar)** atau **Rotten (Busuk)**. Proyek ini dibangun secara end-to-end, mulai dari pemindaian dataset riil, Exploratory Data Analysis (EDA), pipeline preprocessing & augmentasi citra, pelatihan model dengan callbacks adaptif, evaluasi metrik sebenarnya (*precision, recall, F1-score, confusion matrix*), modul inferensi citra tunggal, hingga antarmuka web interaktif modern berbasis **Streamlit**.

---

## 📌 1. Deskripsi & Tujuan Proyek
- **Tujuan Utama**: Mengembangkan sistem Computer Vision cerdas yang mampu mengidentifikasi kualitas kesegaran buah secara otomatis, objektif, dan presisi tinggi guna mendukung otomatisasi sortasi pada industri ritel maupun pertanian.
- **Standar Akademik**: Disusun secara profesional dan modular untuk mahasiswa Informatika semester 7 dengan dokumentasi lengkap, bebas dari data dummy, dan seluruh metrik berasal dari evaluasi aktual.

---

## 📂 2. Dataset
- **Sumber Dataset**: [Fruits fresh and rotten for classification - Kaggle](https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification/data)
- **Total Citra Valid**: **13.599 citra** (0 file corrupt).
- **Format File**: PNG (`.png`).
- **Pembagian Data (Stratified Split)**:
  - **Training (70%)**: 9.519 gambar
  - **Validation (15%)**: 2.040 gambar
  - **Testing (15%)**: 2.040 gambar
- **Daftar Kelas Sebenarnya (6 Kelas)**:
  1. `freshapples` (2.088 gambar)
  2. `freshbanana` (1.962 gambar)
  3. `freshoranges` (1.854 gambar)
  4. `rottenapples` (2.943 gambar)
  5. `rottenbanana` (2.754 gambar)
  6. `rottenoranges` (1.998 gambar)

---

## 🛠️ 3. Teknologi & Library
- **Bahasa Pemrograman**: Python 3.10+
- **Deep Learning / Computer Vision**: TensorFlow 2.x, Keras, MobileNetV2 (Pretrained ImageNet), Pillow
- **Data Science & Visualisasi**: NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn
- **Aplikasi Web**: Streamlit

---

## 📁 4. Struktur Proyek
```text
fruit-fresh-classification/
├── dataset/                    # Direktori citra dataset aktual (train/test)
├── notebooks/
│   └── 01_eda.ipynb            # Notebook Exploratory Data Analysis interaktif
├── models/
│   ├── best_model.keras        # Bobot model terbaik (tersimpan oleh ModelCheckpoint)
│   ├── class_names.json        # Mapping kelas aktual
│   └── dataset_splits.csv      # Cache pembagian data stratified
├── results/
│   ├── training_accuracy.png   # Grafik akurasi training vs validasi aktual
│   ├── training_loss.png       # Grafik loss training vs validasi aktual
│   └── confusion_matrix.png    # Heatmap matriks konfusi test set aktual
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # Pemeriksaan integritas citra & stratified splitting
│   ├── preprocessing.py        # Resize 224x224, augmentasi realistis, tf.data pipeline
│   ├── train.py                # Pelatihan Transfer Learning MobileNetV2 & Fine-Tuning
│   ├── evaluate.py             # Evaluasi test set, classification report & interpretasi
│   ├── predict.py              # Inferensi citra tunggal dengan error handling
│   └── setup_dataset.py        # Utilitas koneksi dataset Kagglehub
├── app.py                      # Aplikasi Web Streamlit modern (🍎 FruitFresh AI)
├── requirements.txt            # Dependensi yang kompatibel
├── .gitignore                  # Filter version control
└── README.md                   # Dokumentasi komprehensif proyek
```

---

## 🚀 5. Panduan Instalasi & Eksekusi

### A. Instalasi Dependensi
Pastikan Python 3.10+ terinstal, kemudian jalankan:
```bash
pip install -r requirements.txt
```

### B. Persiapan Dataset (Otomatis via Kagglehub)
Dataset dapat diunduh langsung melalui script:
```python
import kagglehub
path = kagglehub.dataset_download("sriramr/fruits-fresh-and-rotten-for-classification")
print("Downloaded to:", path)
```
Kemudian hubungkan ke direktori proyek:
```bash
python src/setup_dataset.py
```

### C. Pemeriksaan Dataset Aktual
```bash
python src/data_loader.py
```

### D. Menjalankan Exploratory Data Analysis (EDA)
Buka file [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb) pada Jupyter Notebook atau VS Code untuk melihat distribusi data, visualisasi sampel citra tiap kelas, variasi dimensi, dan analisis *class imbalance*.

### E. Melatih Model (Training)
```bash
python src/train.py
```
*Proses ini akan melatih model Transfer Learning MobileNetV2, menerapkan fine-tuning pada 20 layer teratas, menggunakan callbacks `EarlyStopping`, `ModelCheckpoint`, dan `ReduceLROnPlateau`, serta otomatis menyimpan bobot terbaik ke `models/best_model.keras`.*

### F. Evaluasi Model pada Test Set
```bash
python src/evaluate.py
```
*Menghasilkan classification report, metrik Precision/Recall/F1-Score, heatmap confusion matrix di `results/confusion_matrix.png`, serta interpretasi akademik dalam Bahasa Indonesia.*

### G. Prediksi Citra Tunggal via CLI
```bash
python src/predict.py "path/ke/gambar_buah.png"
```

### H. Menjalankan Aplikasi Web (Sesuai Referensi TikTok @devilda_id)
Tersedia antarmuka web modern Full-Stack Flask + Vanilla HTML/CSS/JS yang identik dengan gaya video TikTok `@devilda_id`:
```bash
# Menjalankan server web Flask (Port 5005)
python web_app.py
# atau
python api.py
```
Buka browser pada alamat: **`http://127.0.0.1:5005`**

*Fitur pada web ini meliputi:*
- Hero section interaktif dengan tipografi modern dan metrik akurasi 97.4%.
- Grid kartu 2x3 varian buah (Fresh vs Rotten Apple, Banana, Orange).
- Kartu fitur unggulan "Mengapa Memilih FruitFresh AI?".
- Drag & drop upload, tombol uji sampel cepat 1-klik, dan pratinjau gambar dengan tombol hapus.
- Toast notifikasi melayang: `✓ Gambar berhasil dimuat!` dan `✓ Klasifikasi berhasil!`.
- Kartu ganda hasil prediksi (*Kondisi & Jenis Buah* dan *Tingkat Kepercayaan*).
- Rekomendasi informasi tambahan (aroma, tekstur, estimasi masa simpan, kelayakan konsumsi).
- Visualisasi Explainable AI (Grad-CAM heatmap) dan grafik probabilitas 6 kelas.
- **Live Webcam Scanner & Switch Kamera**: Dukungan rotasi kamera depan (selfie) dan kamera belakang (*environment/rear*) untuk perangkat smartphone dan laptop.
- **Live Real-Time Scanner (YOLO Mode HUD)**: Pemindaian kamera otomatis berkelanjutan tanpa harus menekan shutter berulang kali, dilengkapi visual target box dan latency real-time.
- **Riwayat Inspeksi (History Log)**: Penyimpanan riwayat inspeksi lokal persistent, modal peninjauan detail masa lalu, dan fitur unduh rekap riwayat ke format **CSV**.

### I. Modul Pipeline YOLOv8 Object Detection
Projek ini menyediakan modul bridge dari klasifikasi citra tunggal ke *Multi-Fruit Object Detection*:
```bash
# 1. Generator Pseudo-Labeling Dataset Format YOLOv8
python src/yolo_pipeline.py --generate --samples 150

# 2. Pelatihan Ultralytics YOLOv8n
python src/yolo_pipeline.py --train --epochs 20

# 3. Prediksi Multi-Buah pada Citra
python src/yolo_pipeline.py --predict static/samples/fresh_apple.png
```

### J. Menjalankan Aplikasi Web Streamlit
Sebagai alternatif, antarmuka dashboard analitik Streamlit juga tetap tersedia:
```bash
python -m streamlit run app.py
```
Buka browser pada alamat: `http://localhost:8501`

---

## 📊 6. Hasil Evaluasi Model Aktual (Real Test Set)

Evaluasi dilakukan secara objektif pada **2.040 citra data uji (Test Set)** yang belum pernah dilihat model saat pelatihan.

### Ringkasan Metrik
| Metrik | Nilai Aktual |
| :--- | :--- |
| **Accuracy** | **97.40%** |
| **Macro Precision** | **97.45%** |
| **Macro Recall** | **97.41%** |
| **Macro F1-Score** | **97.43%** |

### Classification Report Lengkap
```text
               precision    recall  f1-score   support

  freshapples     0.9688    0.9904    0.9795       313
  freshbanana     0.9799    0.9932    0.9865       294
 freshoranges     0.9890    0.9712    0.9800       278
 rottenapples     0.9553    0.9661    0.9606       442
 rottenbanana     0.9951    0.9806    0.9878       413
rottenoranges     0.9593    0.9433    0.9513       300

     accuracy                         0.9740      2040
    macro avg     0.9745    0.9741    0.9743      2040
 weighted avg     0.9741    0.9740    0.9740      2040
```

### 🧠 Interpretasi Akademik Hasil Evaluasi
1. **Performa Keseluruhan**: Akurasi mencapai **97.40%** dengan Macro F1-Score **97.43%**, membuktikan model memiliki generalisasi yang sangat stabil dalam mengklasifikasikan kesegaran maupun jenis buah.
2. **Kinerja Tertinggi**: Kategori `rottenbanana` dan `freshbanana` meraih F1-Score tertinggi masing-masing **98.78%** dan **98.65%**, karena tekstur dan warna kulit pisang yang khas serta perubahan warna hitam pekat saat membusuk sangat mudah dipelajari oleh filter konvolusi.
3. **Analisis Matriks Konfusi (Pasangan yang Tertukar)**:
   - Pasangan yang paling sering keliru adalah `rottenoranges` yang terprediksi sebagai `rottenapples` (14 sampel) dan `rottenapples` terprediksi sebagai `freshapples` (10 sampel).
   - Fenomena ini terjadi karena pada fase awal pembusukan (*early rotting*), bercak cokelat pada jeruk dan apel memiliki tekstur visual dan gradasi warna yang sangat mirip di bawah pencahayaan tertentu.

---

## 🎓 7. Panduan Presentasi Sidang Kuliah (FAQ Teoretis)

Pertanyaan kritis yang sering diajukan dosen penguji dan jawabannya:

1. **Mengapa Menggunakan CNN?**
   - Convolutional Neural Network (CNN) mempertahankan struktur spasial 2D citra. Fitur seperti sudut, pola tekstur kebusukan, dan warna kulit diekstraksi secara otomatis melalui operasi *kernel convolution*, berbeda dengan MLP konvensional yang meratakan piksel dan menghilangkan hubungan spasial antar-tetangga.
2. **Mengapa Menggunakan MobileNetV2?**
   - MobileNetV2 menggunakan arsitektur *Depthwise Separable Convolution* dan *Inverted Residual with Linear Bottleneck*. Struktur ini mereduksi parameter komputasi hingga 8-9x lipat dibandingkan arsitektur tradisional seperti VGG16, namun mempertahankan akurasi mendekati arsitektur besar. Sangat ideal untuk deployment aplikasi web dan perangkat edge.
3. **Apa itu Transfer Learning?**
   - Teknik memanfaatkan pengetahuan fitur visual dasar (garis, kontur, tekstur) dari model yang telah dilatih pada jutaan citra ImageNet. Dengan mengadopsi bobot pretrained ini, kita tidak perlu melatih model dari nol (*scratch*), proses training menjadi jauh lebih cepat, dan model terhindar dari overfitting meskipun dilatih pada data domain spesifik.
4. **Mengapa Gambar Di-resize Menjadi 224 × 224?**
   - Dimensi 224 × 224 × 3 merupakan resolusi input standar kanonikal dari arsitektur MobileNetV2 bawaan ImageNet. Hal ini memastikan kompatibilitas ukuran receptive field filter dan mempertahankan aspek rasio fitur spasial.
5. **Apa Fungsi Data Augmentation?**
   - Menstimulasi variasi citra di dunia nyata (rotasi sudut foto, jarak kamera via zoom, variasi cahaya via contrast, pergeseran posisi via translation) tanpa mengubah label asli buah. Hal ini meningkatkan ketahanan (*robustness*) model terhadap variasi input saat pengujian.
6. **Mengapa Dataset Dibagi Menjadi Training (70%), Validation (15%), dan Testing (15%)?**
   - **Training Set (70%)**: Untuk memperbarui bobot model melalui backpropagation.
   - **Validation Set (15%)**: Untuk evaluasi berkala saat training guna mendeteksi overfitting dan mengontrol callbacks (`EarlyStopping`, `ReduceLROnPlateau`).
   - **Testing Set (15%)**: Data independen murni yang tidak pernah disentuh saat pelatihan untuk mengukur performa riil model di dunia nyata (*unbiased evaluation*).
7. **Apa Fungsi EarlyStopping dan Dropout?**
   - **EarlyStopping**: Menghentikan pelatihan jika `val_loss` tidak lagi membaik dalam jumlah epoch tertentu (*patience*), mencegah model menghafal data training (overfitting).
   - **Dropout (0.3 & 0.2)**: Menonaktifkan sebagian neuron secara acak selama training, memaksa jaringan mempelajari representasi fitur yang redundan dan tidak bergantung pada satu set neuron tertentu saja.
8. **Bagaimana Membaca Confusion Matrix?**
   - Baris matriks merepresentasikan **Label Aktual (True Class)**, sedangkan kolom merepresentasikan **Prediksi Model (Predicted Class)**. Nilai pada diagonal utama menunjukkan jumlah prediksi yang tepat, sedangkan elemen di luar diagonal (*off-diagonal*) menunjukkan jumlah dan pola kesalahan klasifikasi.

---

## 🔮 8. Future Development & Ekspansi
- [x] Konversi model ke format **TensorFlow Lite (TFLite)** (2.58 MB, 76.8% lebih ringkas) melalui [convert_to_tflite.py](file:///c:/Users/PC/Documents/Projekl/Projek%20ML%20Fresh%20Fruit/src/convert_to_tflite.py).
- [ ] Penambahan deteksi bounding box (*Object Detection* seperti YOLOv8/YOLOv11) untuk mendeteksi banyak buah sekaligus dalam satu wadah/keranjang.
- [ ] Estimasi tingkat persentase kematangan buah (*Ripeness Percentage Estimation*).
