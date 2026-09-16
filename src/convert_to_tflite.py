"""
Script convert_to_tflite.py
Mengonversi model Keras ke TensorFlow Lite (TFLite) teroptimasi (Dynamic Range Quantization)
serta membandingkan ukuran file dan latensi inferensi antara Keras vs TFLite.
"""

import time
from pathlib import Path
import numpy as np
import tensorflow as tf

def convert_and_benchmark():
    project_root = Path(__file__).resolve().parent.parent
    keras_path = project_root / "models" / "best_model.keras"
    tflite_path = project_root / "models" / "model.tflite"
    
    if not keras_path.exists():
        print(f"[ERROR] File model {keras_path} tidak ditemukan!")
        return
        
    print("=" * 60)
    print("       KONVERSI MODEL & BENCHMARK TENSORFLOW LITE")
    print("=" * 60)
    
    # 1. Konversi Keras ke TFLite dengan Dynamic Range Quantization
    print("[1/3] Memuat model Keras dan mengonversi ke TFLite...")
    keras_model = tf.keras.models.load_model(str(keras_path))
    converter = tf.lite.TFLiteConverter.from_keras_model(keras_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model_bytes = converter.convert()
    
    with open(tflite_path, "wb") as f:
        f.write(tflite_model_bytes)
        
    keras_size_mb = keras_path.stat().st_size / (1024 * 1024)
    tflite_size_mb = tflite_path.stat().st_size / (1024 * 1024)
    reduction = (1 - tflite_size_mb / keras_size_mb) * 100
    
    print("\n[PERBANDINGAN UKURAN MODEL]")
    print(f"  • Keras Model (.keras)  : {keras_size_mb:.2f} MB")
    print(f"  • TFLite Model (.tflite): {tflite_size_mb:.2f} MB")
    print(f"  • Penghematan Ukuran    : {reduction:.1f}% LEBIH RINGAN!\n")
    
    # 2. Benchmark Kecepatan Inferensi
    print("[2/3] Melakukan benchmark latensi inferensi (50 iterasi)...")
    sample_input = np.random.uniform(-1, 1, size=(1, 224, 224, 3)).astype(np.float32)
    
    # Warm-up Keras
    for _ in range(5):
        _ = keras_model.predict(sample_input, verbose=0)
    start_keras = time.time()
    for _ in range(50):
        _ = keras_model.predict(sample_input, verbose=0)
    keras_latency = (time.time() - start_keras) / 50 * 1000 # ms
    
    # Inisialisasi TFLite Interpreter
    interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Warm-up TFLite
    for _ in range(5):
        interpreter.set_tensor(input_details[0]['index'], sample_input)
        interpreter.invoke()
    start_tflite = time.time()
    for _ in range(50):
        interpreter.set_tensor(input_details[0]['index'], sample_input)
        interpreter.invoke()
        _ = interpreter.get_tensor(output_details[0]['index'])
    tflite_latency = (time.time() - start_tflite) / 50 * 1000 # ms
    
    print("[PERBANDINGAN LATENSI INFERENSI (CPU)]")
    print(f"  • Keras Model Latency  : {keras_latency:.2f} ms per citra")
    print(f"  • TFLite Model Latency : {tflite_latency:.2f} ms per citra")
    speedup = keras_latency / tflite_latency if tflite_latency > 0 else 1.0
    print(f"  • Kecepatan TFLite     : {speedup:.1f}x LEBIH CEPAT!")
    print("=" * 60)
    print(f"[SUKSES] Model TFLite siap digunakan pada perangkat mobile/edge di: {tflite_path}")

if __name__ == "__main__":
    convert_and_benchmark()
