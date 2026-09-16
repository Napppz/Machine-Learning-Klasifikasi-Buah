"""
Module evaluate.py
Evaluasi Komprehensif Model MobileNetV2 pada Test Dataset Nyata (FruitFresh AI)

Penjelasan untuk Presentasi Sidang Kuliah:
1. Accuracy: Rasio total prediksi benar terhadap keseluruhan data uji.
   - Cocok jika persebaran kelas seimbang, namun bisa bias jika terjadi class imbalance.
2. Precision: Dari seluruh citra yang diprediksi sebagai kelas X, berapa persen yang benar-benar kelas X?
   - Mengukur kepastian model agar meminimalkan false positive.
3. Recall (Sensitivity): Dari seluruh citra yang sebenarnya adalah kelas X, berapa persen yang berhasil dikenali oleh model?
   - Mengukur kemampuan model agar tidak melewatkan buah busuk (meminimalkan false negative).
4. F1-Score: Harmonic mean dari precision dan recall.
   - Memberikan keseimbangan objektif antara precision dan recall.
5. Confusion Matrix: Matriks tabel kontingensi N x N yang menunjukkan perbandingan label aktual (baris)
   dengan label prediksi (kolom). Sangat berguna untuk mendeteksi pasangan kelas mana yang sering tertukar.
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import tensorflow as tf

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data_loader import prepare_data_splits
from src.preprocessing import build_tf_dataset

def generate_indonesian_interpretation(conf_mat: np.ndarray, class_names: list, accuracy: float, f1_macro: float) -> str:
    """
    Menghasilkan interpretasi deskriptif otomatis dalam Bahasa Indonesia
    berdasarkan metrik dan kesalahan klasifikasi aktual dari Confusion Matrix.
    """
    num_classes = len(class_names)
    text = []
    text.append("=" * 60)
    text.append("       INTERPRETASI AKADEMIK HASIL EVALUASI (BAHASA INDONESIA)")
    text.append("=" * 60)
    
    # Kategori performa
    if accuracy >= 0.90:
        perf_desc = "sangat tinggi (sangat memuaskan)"
    elif accuracy >= 0.80:
        perf_desc = "baik dan stabil"
    elif accuracy >= 0.70:
        perf_desc = "cukup baik, namun masih memerlukan optimasi lebih lanjut"
    else:
        perf_desc = "kurang optimal dan berpotensi underfitting"
        
    text.append(f"1. Model MobileNetV2 mencapai akurasi keseluruhan sebesar {accuracy*100:.2f}% "
                f"dengan Macro F1-Score sebesar {f1_macro*100:.2f}%. Performa ini tergolong {perf_desc}.")
    
    # Cari pasangan kelas yang paling sering tertukar (off-diagonal)
    errors = []
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j and conf_mat[i, j] > 0:
                errors.append((conf_mat[i, j], class_names[i], class_names[j]))
                
    errors.sort(key=lambda x: x[0], reverse=True)
    
    if errors:
        top_err = errors[0]
        text.append(f"2. Berdasarkan Confusion Matrix, pasangan kelas yang paling sering tertukar adalah:\n"
                    f"   - Label Aktual: '{top_err[1]}' diprediksi keliru sebagai '{top_err[2]}' "
                    f"sebanyak {top_err[0]} sampel.")
        
        # Analisis tambahan jika ada error kedua
        if len(errors) > 1 and errors[1][0] > 0:
            second_err = errors[1]
            text.append(f"   - Pasangan kedua: '{second_err[1]}' diprediksi sebagai '{second_err[2]}' "
                        f"sebanyak {second_err[0]} sampel.")
                        
        text.append("3. Hal ini wajar terjadi dalam domain Computer Vision karena kemiripan tekstur visual, "
                    "gradasi warna pembusukan pada fase awal (early rotting), atau sudut pencahayaan yang mirip.")
    else:
        text.append("2. Confusion Matrix menunjukkan hasil klasifikasi sempurna (tidak terdapat sampel yang tertukar).")
        
    text.append("4. Penggunaan MobileNetV2 dengan bobot pretrained ImageNet terbukti efektif mengekstrak fitur spasial "
                "buah secara efisien tanpa memerlukan komputasi berlebih.")
    text.append("=" * 60)
    
    return "\n".join(text)

def run_evaluation(batch_size: int = 32):
    """Mengevaluasi model pada test dataset secara menyeluruh dan menyimpan visualisasi."""
    print("=" * 60)
    print("         MEMULAI EVALUASI MODEL PADA TEST SET")
    print("=" * 60)
    
    models_dir = project_root / "models"
    model_path = models_dir / "best_model.keras"
    class_names_path = models_dir / "class_names.json"
    
    if not model_path.exists():
        print(f"[ERROR] File model '{model_path}' tidak ditemukan. Jalankan train.py terlebih dahulu.")
        return
        
    if not class_names_path.exists():
        print(f"[ERROR] File '{class_names_path}' tidak ditemukan.")
        return
        
    # 1. Muat mapping kelas dan Model
    with open(class_names_path, "r", encoding="utf-8") as f:
        class_names = json.load(f)
        
    print(f"[INFO] Memuat bobot model terbaik dari: {model_path}")
    model = tf.keras.models.load_model(str(model_path))
    
    # 2. Siapkan Test Dataset
    df_all = prepare_data_splits()
    if df_all is None:
        print("[ERROR] Gagal memuat dataset untuk testing.")
        return
        
    test_df = df_all[df_all['split'] == 'test']
    print(f"[INFO] Menguji model pada {len(test_df)} sampel test...")
    
    test_ds = build_tf_dataset(test_df, batch_size=batch_size, is_training=False)
    
    # 3. Prediksi Batch
    y_true = test_df['label'].values
    y_pred_probs = model.predict(test_ds, verbose=1)
    y_pred = np.argmax(y_pred_probs, axis=1)
    
    # 4. Hitung Metrik Evaluasi Nyata
    accuracy = accuracy_score(y_true, y_pred)
    precision_macro = precision_score(y_true, y_pred, average="macro", zero_division=0)
    recall_macro = recall_score(y_true, y_pred, average="macro", zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    
    print("\n" + "=" * 60)
    print("                 RINGKASAN METRIK EVALUASI NYATA")
    print("=" * 60)
    print(f"Accuracy  : {accuracy * 100:.2f}%")
    print(f"Precision : {precision_macro * 100:.2f}% (Macro Average)")
    print(f"Recall    : {recall_macro * 100:.2f}% (Macro Average)")
    print(f"F1-Score  : {f1_macro * 100:.2f}% (Macro Average)")
    print("-" * 60)
    print("\nCLASSIFICATION REPORT LENGKAP:\n")
    print(classification_report(y_true, y_pred, target_names=class_names, digits=4))
    
    # 5. Plot & Simpan Confusion Matrix
    conf_mat = confusion_matrix(y_true, y_pred)
    results_dir = project_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(9, 7))
    sns.heatmap(
        conf_mat, 
        annot=True, 
        fmt="d", 
        cmap="Blues", 
        xticklabels=class_names, 
        yticklabels=class_names,
        cbar=True
    )
    plt.title("Confusion Matrix Uji Coba Aktual (FruitFresh AI)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Predicted Class (Prediksi Model)", fontsize=11, labelpad=8)
    plt.ylabel("True Class (Label Sebenarnya)", fontsize=11, labelpad=8)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    cm_path = results_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"[INFO] Confusion Matrix heatmap tersimpan di: {cm_path}")
    
    # 6. Cetak Interpretasi Bahasa Indonesia
    interpretation = generate_indonesian_interpretation(conf_mat, class_names, accuracy, f1_macro)
    print("\n" + interpretation)

if __name__ == "__main__":
    run_evaluation()
