"""
yolo_pipeline.py - Modul Konversi & Arsitektur YOLOv8 (FruitFresh AI)
-------------------------------------------------------------------------
Modul ini menghubungkan pipeline klasifikasi citra ke Object Detection (YOLOv8).
Menyediakan:
1. Auto-generator anotasi Bounding Box (Pseudo-Labeling via Otsu Foreground Saliency)
2. Konfigurasi dataset YOLOv8 (data.yaml)
3. Template Pelatihan Ultralytics YOLOv8n (Multi-Fruit in 1 Image)
4. Fungsi Inferensi Bounding Box untuk mendeteksi banyak buah sekaligus dalam 1 frame
"""

import os
import sys
import glob
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CLASS_NAMES = [
    "freshapples",
    "freshbanana",
    "freshoranges",
    "rottenapples",
    "rottenbanana",
    "rottenoranges"
]
CLASS_TO_IDX = {name: i for i, name in enumerate(CLASS_NAMES)}

def extract_fruit_bounding_box(pil_img: Image.Image) -> Tuple[float, float, float, float]:
    """
    Ekstraksi estimasi bounding box objek buah menggunakan thresholding intensitas
    dan deteksi kontur foreground (Pseudo-Labeling).
    Mengembalikan koordinat ternormalisasi format YOLO:
    (x_center, y_center, width, height) rentang 0.0 - 1.0.
    """
    w, h = pil_img.size
    # Konversi ke Grayscale untuk analisis kontras latar belakang
    gray = pil_img.convert("L")
    arr = np.array(gray)
    
    # Deteksi tepi / thresholding non-background
    # Gambar dataset Kaggle umumnya berlatar putih/terang atau netral
    # Buah biasanya memiliki intensitas yang berbeda dari 4 sudut gambar
    corners = [arr[0, 0], arr[0, -1], arr[-1, 0], arr[-1, -1]]
    bg_mean = float(np.mean(corners))
    
    if bg_mean > 128:
        # Latar belakang terang -> buah lebih gelap
        mask = arr < (bg_mean - 28)
    else:
        # Latar belakang gelap -> buah lebih terang
        mask = arr > (bg_mean + 28)
        
    y_indices, x_indices = np.where(mask)
    
    if len(x_indices) > 50 and len(y_indices) > 50:
        # Tentukan batas ekstrim dengan margin keamanan 3%
        x_min = max(0, float(np.min(x_indices)))
        x_max = min(w, float(np.max(x_indices)))
        y_min = max(0, float(np.min(y_indices)))
        y_max = min(h, float(np.max(y_indices)))
    else:
        # Fallback tengah gambar (tight center crop 80%)
        x_min = w * 0.1
        x_max = w * 0.9
        y_min = h * 0.1
        y_max = h * 0.9
        
    # Hitung nilai ternormalisasi YOLO
    box_w = (x_max - x_min) / w
    box_h = (y_max - y_min) / h
    x_c = (x_min + x_max) / (2.0 * w)
    y_c = (y_min + y_max) / (2.0 * h)
    
    # Batasi nilai aman 0.0 - 1.0
    x_c = min(max(x_c, 0.05), 0.95)
    y_c = min(max(y_c, 0.05), 0.95)
    box_w = min(max(box_w, 0.1), 0.98)
    box_h = min(max(box_h, 0.1), 0.98)
    
    return x_c, y_c, box_w, box_h

def generate_yolo_dataset(output_dir: str = "dataset_yolo", sample_limit_per_class: int = 150):
    """
    Mengonversi sampel dataset klasifikasi yang ada ke format dataset YOLOv8:
    dataset_yolo/
      images/train/, images/val/
      labels/train/, labels/val/
      data.yaml
    """
    out_path = PROJECT_ROOT / output_dir
    train_img_dir = out_path / "images" / "train"
    val_img_dir = out_path / "images" / "val"
    train_lbl_dir = out_path / "labels" / "train"
    val_lbl_dir = out_path / "labels" / "val"
    
    for d in [train_img_dir, val_img_dir, train_lbl_dir, val_lbl_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    dataset_source = PROJECT_ROOT / "dataset"
    if not dataset_source.exists():
        print(f"[ERROR] Direktori dataset tidak ditemukan di: {dataset_source}")
        return
        
    print(f"\n[YOLO Pipeline] Memulai konversi pseudo-labeling dataset YOLO ke: {out_path}")
    total_processed = 0
    
    for class_name in CLASS_NAMES:
        class_id = CLASS_TO_IDX[class_name]
        # Cari citra di train dan test
        pattern1 = str(dataset_source / "train" / class_name / "*.png")
        pattern2 = str(dataset_source / "test" / class_name / "*.png")
        files = glob.glob(pattern1) + glob.glob(pattern2)
        
        if not files:
            # Fallback jika struktur flat
            pattern_flat = str(dataset_source / class_name / "*.png")
            files = glob.glob(pattern_flat)
            
        np.random.seed(42)
        np.random.shuffle(files)
        selected_files = files[:sample_limit_per_class]
        
        print(f"  -> Memproses kelas '{class_name}' ({len(selected_files)} citra)...")
        
        for idx, fpath in enumerate(selected_files):
            try:
                img = Image.open(fpath)
                # Split 80% train, 20% val
                is_val = (idx % 5 == 0)
                dest_img_dir = val_img_dir if is_val else train_img_dir
                dest_lbl_dir = val_lbl_dir if is_val else train_lbl_dir
                
                base_name = f"{class_name}_{idx:04d}"
                out_img_path = dest_img_dir / f"{base_name}.jpg"
                out_lbl_path = dest_lbl_dir / f"{base_name}.txt"
                
                # Simpan citra JPG standar YOLO
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(out_img_path, "JPEG", quality=90)
                
                # Ekstraksi Bounding Box
                xc, yc, bw, bh = extract_fruit_bounding_box(img)
                
                # Tulis file anotasi YOLO txt: <class_idx> <x_center> <y_center> <width> <height>
                with open(out_lbl_path, "w", encoding="utf-8") as f:
                    f.write(f"{class_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
                    
                total_processed += 1
            except Exception as e:
                print(f"     [Warning] Gagal memproses file {fpath}: {e}")
                
    # Buat data.yaml
    yaml_content = f"""# FruitFresh AI - YOLOv8 Dataset Configuration
path: {out_path.as_posix()}
train: images/train
val: images/val

names:
  0: freshapples
  1: freshbanana
  2: freshoranges
  3: rottenapples
  4: rottenbanana
  5: rottenoranges
"""
    yaml_path = out_path / "data.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
        
    print(f"\n[SUKSES] Dataset YOLO berhasil dibuat! Total {total_processed} citra teranotasi.")
    print(f"File konfigurasi tersimpan di: {yaml_path}")
    print("\nUntuk melatih model YOLOv8n:")
    print(f"  yolo task=detect mode=train model=yolov8n.pt data={yaml_path.as_posix()} epochs=25 imgsz=640")

def train_yolov8(data_yaml_path: str = None, epochs: int = 20, imgsz: int = 640):
    """
    Menjalankan pelatihan Ultralytics YOLOv8.
    Memerlukan library 'ultralytics': pip install ultralytics
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("\n[PERINGATAN] Library 'ultralytics' belum terinstal.")
        print("Silakan jalankan: pip install ultralytics\n")
        return
        
    if data_yaml_path is None:
        data_yaml_path = str(PROJECT_ROOT / "dataset_yolo" / "data.yaml")
        
    if not Path(data_yaml_path).exists():
        print(f"[ERROR] File konfigurasi YOLO tidak ditemukan di: {data_yaml_path}")
        print("Harap jalankan generator dataset terlebih dahulu: python src/yolo_pipeline.py --generate")
        return
        
    print("\n=======================================================")
    print(" [FruitFresh AI] Memulai Pelatihan Ultralytics YOLOv8n")
    print(f" Data Config: {data_yaml_path}")
    print(f" Epochs: {epochs} | Image Size: {imgsz}")
    print("=======================================================\n")
    
    model = YOLO("yolov8n.pt")  # Nano model (ringan dan cepat)
    results = model.train(
        data=data_yaml_path,
        epochs=epochs,
        imgsz=imgsz,
        project=str(PROJECT_ROOT / "results_yolo"),
        name="fruitfresh_yolo",
        save=True
    )
    print("\n[SUKSES] Pelatihan YOLOv8 selesai!")
    return results

def detect_multi_fruit(image_path: str, model_path: str = None) -> List[Dict[str, Any]]:
    """
    Melakukan deteksi multi-buah pada citra tunggal menggunakan YOLOv8.
    Mengembalikan daftar objek yang terdeteksi dengan bounding box.
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] Library 'ultralytics' belum terpasang.")
        return []
        
    if model_path is None:
        best_pt = PROJECT_ROOT / "results_yolo" / "fruitfresh_yolo" / "weights" / "best.pt"
        if best_pt.exists():
            model_path = str(best_pt)
        else:
            model_path = "yolov8n.pt"  # Pretrained ImageNet/COCO fallback
            
    model = YOLO(model_path)
    results = model(image_path)
    
    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            
            label = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else f"class_{cls_id}"
            detections.append({
                "label": label,
                "confidence": round(conf * 100, 2),
                "is_fresh": "fresh" in label.lower(),
                "box": [round(coord, 1) for coord in xyxy]
            })
            
    return detections

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FruitFresh AI - YOLOv8 Conversion & Training Pipeline")
    parser.add_argument("--generate", action="store_true", help="Generate pseudo-labeled YOLO dataset from existing data")
    parser.add_argument("--train", action="store_true", help="Train Ultralytics YOLOv8 model")
    parser.add_argument("--epochs", type=int, default=20, help="Number of training epochs")
    parser.add_argument("--samples", type=int, default=120, help="Sample count per class for YOLO dataset")
    parser.add_argument("--predict", type=str, help="Run detection on a fruit image")
    
    args = parser.parse_args()
    
    if args.generate:
        generate_yolo_dataset(sample_limit_per_class=args.samples)
    elif args.train:
        train_yolov8(epochs=args.epochs)
    elif args.predict:
        dets = detect_multi_fruit(args.predict)
        print("\n[Hasil Deteksi Multi-Buah YOLO]:")
        print(json.dumps(dets, indent=2))
    else:
        print("\n=======================================================")
        print(" FruitFresh AI — YOLOv8 Object Detection Pipeline")
        print("=======================================================")
        print("Perintah yang tersedia:")
        print("  1. Buat dataset YOLO dari data saat ini:")
        print("     python src/yolo_pipeline.py --generate --samples 150")
        print("  2. Latih model YOLOv8:")
        print("     python src/yolo_pipeline.py --train --epochs 20")
        print("  3. Deteksi multi-buah pada foto:")
        print("     python src/yolo_pipeline.py --predict static/samples/fresh_apple.png")
        print("=======================================================\n")
