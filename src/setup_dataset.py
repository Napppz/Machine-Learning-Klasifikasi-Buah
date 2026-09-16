"""
Script setup_dataset.py
Menghubungkan dataset yang diunduh melalui kagglehub ke folder 'dataset/' pada proyek.
Mendukung Directory Junction di Windows agar tidak menduplikasi 3.58 GB file ke disk,
serta mendukung copy fallback jika diperlukan.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def setup_downloaded_dataset(kagglehub_path: str = None):
    project_root = Path(__file__).resolve().parent.parent
    target_dataset_dir = project_root / "dataset"
    
    # Jika path tidak diberikan, cari di cache standar kagglehub
    if not kagglehub_path:
        default_cache = Path.home() / ".cache" / "kagglehub" / "datasets" / "sriramr" / "fruits-fresh-and-rotten-for-classification"
        if default_cache.exists():
            versions = [v for v in default_cache.iterdir() if v.is_dir()]
            if versions:
                latest_version = sorted(versions, key=lambda x: x.stat().st_mtime, reverse=True)[0]
                kagglehub_path = str(latest_version)
                
    if not kagglehub_path or not Path(kagglehub_path).exists():
        print(f"[ERROR] Path dataset kagglehub tidak ditemukan: {kagglehub_path}")
        return False
        
    src_path = Path(kagglehub_path)
    print(f"[INFO] Sumber dataset: {src_path}")
    print(f"[INFO] Target folder: {target_dataset_dir}")
    
    # Cek struktur di dalam src_path
    subdirs = [d for d in src_path.iterdir() if d.is_dir()]
    print(f"[INFO] Subdirektori di sumber: {[d.name for d in subdirs]}")
    
    # Cari folder utama dataset jika terdapat subfolder bersarang (misal dataset/dataset)
    actual_data_src = src_path
    if len(subdirs) == 1 and subdirs[0].name.lower() in {"dataset", "fruits-fresh-and-rotten-for-classification"}:
        actual_data_src = subdirs[0]
        
    # Buat directory junction atau hubungkan folder
    # Bersihkan .gitkeep jika perlu atau buat link ke isi dataset
    for item in actual_data_src.iterdir():
        dest_item = target_dataset_dir / item.name
        if not dest_item.exists():
            if item.is_dir():
                print(f"[LINK] Menghubungkan direktori '{item.name}' ke folder dataset/...")
                try:
                    # Buat Junction di Windows (cepat, 0 space, tanpa admin)
                    subprocess.run(
                        ["cmd", "/c", "mklink", "/J", str(dest_item), str(item)],
                        check=True,
                        capture_output=True
                    )
                    print(f"       -> Sukses membuat Directory Junction: {item.name}")
                except Exception as e:
                    print(f"       -> Junction gagal, menyalin folder: {item.name}...")
                    shutil.copytree(item, dest_item)
            else:
                shutil.copy2(item, dest_item)
                
    print("[SUCCESS] Dataset berhasil disiapkan di folder 'dataset/'!")
    return True

if __name__ == "__main__":
    path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    setup_downloaded_dataset(path_arg)
