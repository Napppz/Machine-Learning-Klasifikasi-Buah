"""
Module data_loader.py
Bertanggung jawab untuk:
1. Memeriksa keberadaan dataset di folder 'dataset/'
2. Mendeteksi struktur folder secara otomatis (flat atau train/test split bawaan)
3. Mengekstrak nama class secara dinamis (tanpa hardcoding)
4. Memvalidasi integritas gambar (mendeteksi file corrupt menggunakan PIL)
5. Menghitung statistik dataset (jumlah per class, total gambar, ekstensi file)
6. Membagi data menjadi 70% Train, 15% Validation, 15% Test dengan stratifikasi
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image
import pandas as pd

# Ekstensi gambar yang didukung secara umum
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

def get_project_root() -> Path:
    """Mengembalikan root path project secara relatif/independen terhadap environment."""
    return Path(__file__).resolve().parent.parent

def find_dataset_dir(base_dir: Optional[Path] = None) -> Tuple[Optional[Path], str]:
    """
    Mencari direktori dataset di bawah folder 'dataset/'.
    Mendukung berbagai struktur ekstraksi dari Kaggle (misal subfolder bersarang).
    """
    if base_dir is None:
        base_dir = get_project_root() / "dataset"
        
    if not base_dir.exists():
        return None, "Folder 'dataset/' tidak ditemukan."
    
    # Cek apakah ada file zip yang belum diekstrak
    zip_files = list(base_dir.glob("*.zip"))
    if zip_files:
        return base_dir, f"Ditemukan file arsip {zip_files[0].name}. Perlu diekstrak terlebih dahulu."

    # Periksa apakah ada subdirektori
    subdirs = [d for d in base_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    if not subdirs:
        return None, "Folder 'dataset/' masih kosong. Belum ada dataset yang dimasukkan."
    
    # Jika terdapat subfolder train/test di dalam dataset/
    subdir_names = [d.name.lower() for d in subdirs]
    if "train" in subdir_names:
        return base_dir, "Struktur train/test terdeteksi di dalam 'dataset/'."
    
    # Cek jika ada folder bersarang hasil ekstraksi (misal dataset/Fruits_Dataset/...)
    if len(subdirs) == 1 and ("dataset" in subdirs[0].name.lower() or "fruit" in subdirs[0].name.lower()):
        nested_subdirs = [d for d in subdirs[0].iterdir() if d.is_dir() and not d.name.startswith('.')]
        nested_names = [d.name.lower() for d in nested_subdirs]
        if "train" in nested_names or any(len(list(d.glob('*.*'))) > 0 for d in nested_subdirs):
            return subdirs[0], f"Dataset ditemukan di dalam subfolder bersarang: {subdirs[0].name}"

    # Jika langsung berisi folder kelas
    return base_dir, "Dataset ditemukan langsung di dalam folder 'dataset/'."

def inspect_dataset(dataset_dir: Optional[Path] = None) -> Dict:
    """
    Memeriksa seluruh gambar di dataset:
    - Nama class yang ditemukan
    - Jumlah gambar per class
    - Total gambar
    - Ekstensi file
    - File yang korup / rusak
    """
    if dataset_dir is None:
        dataset_dir, msg = find_dataset_dir()
        if dataset_dir is None:
            return {"status": "NOT_FOUND", "message": msg}
        
    print(f"\n[INFO] Memindai dataset pada direktori: {dataset_dir}")
    
    # Kumpulkan seluruh file gambar dan telusuri class
    image_paths: List[Path] = []
    class_map: Dict[str, List[Path]] = {}
    corrupted_files: List[Tuple[str, str]] = []
    extension_counts: Dict[str, int] = {}
    
    # Scan rekursif untuk menemukan seluruh gambar
    for root, _, files in os.walk(dataset_dir):
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            
            # Catat ekstensi
            extension_counts[ext] = extension_counts.get(ext, 0) + 1
            
            if ext in VALID_EXTENSIONS:
                # Tentukan nama kelas dari nama parent folder
                # Jika berada di bawah train/freshapples, nama kelas adalah freshapples
                class_name = file_path.parent.name
                
                # Jika parent bernama train/test/val, gunakan nama grandparent jika relevan
                if class_name.lower() in {"train", "test", "val", "validation"}:
                    continue
                    
                if class_name not in class_map:
                    class_map[class_name] = []
                
                # Validasi integritas gambar dengan Pillow
                try:
                    with Image.open(file_path) as img:
                        img.verify() # Memastikan header dan struktur gambar valid
                    class_map[class_name].append(file_path)
                    image_paths.append(file_path)
                except Exception as e:
                    corrupted_files.append((str(file_path), str(e)))

    class_names = sorted(list(class_map.keys()))
    class_counts = {cls: len(paths) for cls, paths in class_map.items()}
    total_valid_images = sum(class_counts.values())
    
    result = {
        "status": "OK" if total_valid_images > 0 else "EMPTY",
        "dataset_path": str(dataset_dir),
        "class_names": class_names,
        "num_classes": len(class_names),
        "class_counts": class_counts,
        "total_images": total_valid_images,
        "extensions": extension_counts,
        "corrupted_count": len(corrupted_files),
        "corrupted_files": corrupted_files
    }
    
    return result

def print_dataset_summary(summary: Dict):
    """Mencetak ringkasan pemeriksaan dataset dalam format yang rapi dan profesional."""
    print("=" * 60)
    print("        LAPORAN PEMERIKSAAN DATASET BUAH (FruitFresh AI)")
    print("=" * 60)
    
    if summary.get("status") == "NOT_FOUND":
        print(f"[STATUS] : DATASET BELUM TERSEDIA")
        print(f"[PESAN]  : {summary.get('message')}")
        print("-" * 60)
        print("PANDUAN PENYIAPAN DATASET:")
        print("1. Kunjungi: https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification/data")
        print("2. Unduh dataset (ZIP file).")
        print("3. Ekstrak isinya ke dalam folder 'dataset/' pada proyek ini.")
        print("=" * 60)
        return

    if summary.get("status") == "EMPTY":
        print("[STATUS] : FOLDER TERDETEKSI TETAPI TIDAK DITEMUKAN GAMBAR VALID")
        print(f"Path     : {summary.get('dataset_path')}")
        print("=" * 60)
        return

    print(f"Lokasi Dataset : {summary['dataset_path']}")
    print(f"Jumlah Class   : {summary['num_classes']}")
    print(f"Daftar Class   : {', '.join(summary['class_names'])}")
    print(f"Total Gambar   : {summary['total_images']:,} file")
    print("-" * 60)
    print("DISTRIBUSI GAMBAR PER CLASS:")
    for cls, count in summary['class_counts'].items():
        percentage = (count / summary['total_images'] * 100) if summary['total_images'] > 0 else 0
        print(f"  • {cls:<20} : {count:>5} gambar ({percentage:>5.1f}%)")
    print("-" * 60)
    print("DISTRIBUSI EKSTENSI FILE:")
    for ext, count in summary['extensions'].items():
        print(f"  • {ext or '[tanpa ekstensi]':<10} : {count} file")
    print("-" * 60)
    print(f"File Corrupt/Rusak : {summary['corrupted_count']} file")
    if summary['corrupted_count'] > 0:
        print("Daftar file corrupt:")
        for path, err in summary['corrupted_files'][:5]:
            print(f"  - {path}: {err}")
    print("=" * 60)

def prepare_data_splits(test_size: float = 0.15, val_size: float = 0.15, random_state: int = 42) -> Optional[Any]:
    """
    Mengumpulkan seluruh file gambar dan membaginya menjadi:
    Train (70%), Validation (15%), Test (15%) dengan stratifikasi.
    Mengembalikan DataFrame dengan kolom: ['filepath', 'label', 'class_name', 'split']
    """
    dataset_dir, msg = find_dataset_dir()
    if dataset_dir is None:
        print(f"[ERROR] {msg}")
        return None
        
    summary = inspect_dataset(dataset_dir)
    if summary.get("status") != "OK":
        print("[ERROR] Dataset tidak valid untuk dilakukan pembagian data.")
        return None
        
    data = []
    class_to_idx = {cls: idx for idx, cls in enumerate(summary['class_names'])}
    
    for root, _, files in os.walk(dataset_dir):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in VALID_EXTENSIONS:
                class_name = file_path.parent.name
                if class_name in class_to_idx:
                    data.append({
                        'filepath': str(file_path.resolve()),
                        'class_name': class_name,
                        'label': class_to_idx[class_name]
                    })
                    
    df = pd.DataFrame(data)
    
    # Lakukan Stratified Split: Train 70%, Val 15%, Test 15%
    split_csv_path = get_project_root() / "models" / "dataset_splits.csv"
    if split_csv_path.exists():
        cached_df = pd.read_csv(split_csv_path)
        if len(cached_df) == len(df):
            print(f"\n[INFO] Memuat pembagian dataset dari cache: {split_csv_path}")
            return cached_df

    from sklearn.model_selection import train_test_split
    
    # Split 1: Pisahkan Test (15%) dari sisanya (85%)
    train_val_df, test_df = train_test_split(
        df, 
        test_size=test_size, 
        stratify=df['label'], 
        random_state=random_state
    )
    
    # Split 2: Dari 85%, ambil Validation (15% dari total = 0.15 / 0.85 ≈ 0.1765)
    val_relative_size = val_size / (1.0 - test_size)
    train_df, val_df = train_test_split(
        train_val_df, 
        test_size=val_relative_size, 
        stratify=train_val_df['label'], 
        random_state=random_state
    )
    
    train_df = train_df.copy()
    val_df = val_df.copy()
    test_df = test_df.copy()
    
    train_df['split'] = 'train'
    val_df['split'] = 'val'
    test_df['split'] = 'test'
    
    full_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    
    # Simpan ke CSV untuk konsistensi antara training dan evaluasi
    split_csv_path.parent.mkdir(parents=True, exist_ok=True)
    full_df.to_csv(split_csv_path, index=False)
    
    print(f"\n[INFO] Pembagian dataset selesai dan tersimpan di: {split_csv_path}")
    print(f"  • Training   : {len(train_df)} sampel ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  • Validation : {len(val_df)} sampel ({len(val_df)/len(df)*100:.1f}%)")
    print(f"  • Testing    : {len(test_df)} sampel ({len(test_df)/len(df)*100:.1f}%)")
    
    return full_df

if __name__ == "__main__":
    summary = inspect_dataset()
    print_dataset_summary(summary)
