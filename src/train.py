"""
Module train.py
Pelatihan Model Klasifikasi Kualitas/Kesegaran Buah (FruitFresh AI)
Menggunakan Transfer Learning MobileNetV2 Pretrained ImageNet

Penjelasan untuk Presentasi Sidang Kuliah:
1. Mengapa CNN?
   - Convolutional Neural Network (CNN) memiliki kemampuan mengekstrak fitur spasial
     (pola garis, tekstur kebusukan, warna kulit, bercak) secara hierarkis dari citra,
     jauh lebih unggul dibandingkan neural network konvensional (MLP).
2. Mengapa MobileNetV2?
   - MobileNetV2 menggunakan arsitektur Depthwise Separable Convolution dan Inverted Residuals
     dengan Linear Bottlenecks. Sangat efisien, ringan, cepat, dan akurasi tinggi pada perangkat
     edge / web browser tanpa mengorbankan kualitas prediksi.
3. Apa itu Transfer Learning?
   - Memanfaatkan bobot (weights) yang telah dilatih pada jutaan gambar ImageNet.
     Model sudah memahami fitur visual umum (sudut, gradasi, tekstur), sehingga proses
     training pada dataset buah membutuhkan data dan waktu jauh lebih sedikit dengan akurasi maksimal.
4. Fungsi Callbacks:
   - EarlyStopping: Mencegah overfitting dengan menghentikan training saat val_loss tidak membaik.
   - ModelCheckpoint: Memastikan hanya model dengan val_accuracy tertinggi yang disimpan.
   - ReduceLROnPlateau: Menurunkan learning rate secara adaptif saat konvergensi melambat.
"""

import os
import sys
import json
from pathlib import Path
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks

# Pastikan import lokal dari modul src dapat diakses
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data_loader import inspect_dataset, prepare_data_splits, print_dataset_summary
from src.preprocessing import build_tf_dataset, IMAGE_SIZE

def build_model(num_classes: int, input_shape: tuple = (224, 224, 3), learning_rate: float = 1e-3) -> tf.keras.Model:
    """
    Membangun arsitektur Transfer Learning MobileNetV2:
    Input (224, 224, 3)
      ↓
    MobileNetV2 Base (Pretrained ImageNet, include_top=False, Frozen)
      ↓
    GlobalAveragePooling2D (Mengurangi dimensi spasial menjadi vector 1D)
      ↓
    BatchNormalization (Menstabilkan distribusi aktivasi)
      ↓
    Dropout (0.3) (Regularisasi untuk mencegah overfitting)
      ↓
    Dense (128, activation='relu') (Dense representasi spesifik tugas buah)
      ↓
    Dropout (0.2)
      ↓
    Output Layer (Dense(num_classes, activation='softmax'))
    """
    print(f"\n[INFO] Membangun arsitektur Transfer Learning MobileNetV2 untuk {num_classes} classes...")
    
    # 1. Base Model: MobileNetV2 ImageNet
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False, # Membuang layer klasifikasi 1000-class bawaan ImageNet
        weights='imagenet'
    )
    
    # Bekukan seluruh layer dasar pada tahap awal (Feature Extraction)
    base_model.trainable = False
    
    # 2. Arsitektur Head Baru
    inputs = layers.Input(shape=input_shape, name="input_image")
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="batch_norm")(x)
    x = layers.Dropout(0.3, name="dropout_1")(x)
    x = layers.Dense(128, activation="relu", name="dense_features")(x)
    x = layers.Dropout(0.2, name="dropout_2")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="output_probabilities")(x)
    
    model = models.Model(inputs, outputs, name="FruitFresh_MobileNetV2")
    
    # Kompilasi model dengan Sparse Categorical Crossentropy karena label bertipe integer
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    return model

def plot_training_history(history, results_dir: Path):
    """Menyimpan grafik metrik akurasi dan loss training vs validasi aktual."""
    results_dir.mkdir(parents=True, exist_ok=True)
    
    acc = history.history.get('accuracy', [])
    val_acc = history.history.get('val_accuracy', [])
    loss = history.history.get('loss', [])
    val_loss = history.history.get('val_loss', [])
    epochs_range = range(1, len(acc) + 1)
    
    # 1. Grafik Akurasi
    plt.figure(figsize=(8, 5))
    plt.plot(epochs_range, acc, 'b-o', label='Training Accuracy')
    plt.plot(epochs_range, val_acc, 'g--s', label='Validation Accuracy')
    plt.title('Grafik Akurasi Training vs Validasi (FruitFresh AI)', fontsize=12, fontweight='bold')
    plt.xlabel('Epochs', fontsize=10)
    plt.ylabel('Accuracy', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='lower right')
    plt.tight_layout()
    acc_path = results_dir / "training_accuracy.png"
    plt.savefig(acc_path, dpi=300)
    plt.close()
    print(f"[INFO] Grafik akurasi tersimpan di: {acc_path}")
    
    # 2. Grafik Loss
    plt.figure(figsize=(8, 5))
    plt.plot(epochs_range, loss, 'r-o', label='Training Loss')
    plt.plot(epochs_range, val_loss, 'm--s', label='Validation Loss')
    plt.title('Grafik Loss Training vs Validasi (FruitFresh AI)', fontsize=12, fontweight='bold')
    plt.xlabel('Epochs', fontsize=10)
    plt.ylabel('Loss', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper right')
    plt.tight_layout()
    loss_path = results_dir / "training_loss.png"
    plt.savefig(loss_path, dpi=300)
    plt.close()
    print(f"[INFO] Grafik loss tersimpan di: {loss_path}")

def run_training(epochs: int = 6, batch_size: int = 32, fine_tune_epochs: int = 3):
    """Pipeline training lengkap: persiapan data, kompilasi, training, callbacks, dan fine-tuning."""
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    print("=" * 60)
    print("      MEMULAI PROSES TRAINING MODEL (FruitFresh AI)")
    print("=" * 60)
    
    # 1. Periksa Dataset
    summary = inspect_dataset()
    print_dataset_summary(summary)
    if summary.get("status") != "OK":
        print("\n[STOP] Pelatihan dihentikan karena dataset belum siap.")
        return
        
    class_names = summary['class_names']
    num_classes = len(class_names)
    
    # Simpan class_names.json ke direktori models/
    models_dir = project_root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    class_names_path = models_dir / "class_names.json"
    with open(class_names_path, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)
    print(f"[INFO] Pemetaan kelas tersimpan di: {class_names_path}")
    
    # 2. Split Dataset (70% Train, 15% Val, 15% Test)
    df_all = prepare_data_splits()
    if df_all is None:
        return
        
    train_df = df_all[df_all['split'] == 'train']
    val_df = df_all[df_all['split'] == 'val']
    
    # 3. Bangun tf.data.Dataset
    train_ds = build_tf_dataset(train_df, batch_size=batch_size, is_training=True)
    val_ds = build_tf_dataset(val_df, batch_size=batch_size, is_training=False)
    
    # 4. Bangun Model
    model = build_model(num_classes=num_classes)
    model.summary()
    
    # 5. Konfigurasi Callbacks
    best_model_path = models_dir / "best_model.keras"
    cb_checkpoint = callbacks.ModelCheckpoint(
        filepath=str(best_model_path),
        monitor="val_accuracy",
        mode="max",
        save_best_only=True,
        verbose=1
    )
    
    cb_earlystop = callbacks.EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True,
        verbose=1
    )
    
    cb_reducelr = callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.2,
        patience=2,
        min_lr=1e-6,
        verbose=1
    )
    
    # 6. Tahap 1: Initial Training (Frozen Base)
    print(f"\n[TAHAP 1] Pelatihan Feature Extraction ({epochs} epochs)...")
    history_initial = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=[cb_checkpoint, cb_earlystop, cb_reducelr]
    )
    
    # 7. Tahap 2: Fine-Tuning (Membuka 20 layer teratas MobileNetV2)
    print("\n[TAHAP 2] Membuka layer atas MobileNetV2 untuk Fine-Tuning...")
    base_model = None
    for layer in model.layers:
        if "mobilenetv2" in layer.name.lower():
            base_model = layer
            break
            
    if base_model is not None:
        base_model.trainable = True
        # Bekukan semua layer kecuali 20 layer terakhir
        for layer in base_model.layers[:-20]:
            layer.trainable = False
            
        # Re-compile dengan learning rate sangat kecil untuk fine-tuning
        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-5),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"]
        )
        
        initial_epochs_run = len(history_initial.history['accuracy'])
        total_epochs = initial_epochs_run + fine_tune_epochs
        
        print(f"[INFO] Melanjutkan Fine-Tuning hingga epoch ke-{total_epochs}...")
        history_fine = model.fit(
            train_ds,
            validation_data=val_ds,
            initial_epoch=initial_epochs_run,
            epochs=total_epochs,
            callbacks=[cb_checkpoint, cb_earlystop, cb_reducelr]
        )
        
        # Gabungkan riwayat metrik
        combined_history = type('History', (), {'history': {}})()
        for k in history_initial.history.keys():
            combined_history.history[k] = history_initial.history[k] + history_fine.history.get(k, [])
    else:
        combined_history = history_initial
        
    # 8. Simpan Visualisasi Hasil Training Aktual
    results_dir = project_root / "results"
    plot_training_history(combined_history, results_dir)
    print("\n[SUKSES] Seluruh proses pelatihan selesai dengan hasil riil!")

if __name__ == "__main__":
    run_training()
