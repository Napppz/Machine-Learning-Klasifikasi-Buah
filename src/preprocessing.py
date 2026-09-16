"""
Module preprocessing.py
Bertanggung jawab untuk:
1. Menentukan dimensi input standar MobileNetV2: (224, 224, 3)
2. Pipeline Data Augmentation realistis (RandomFlip, RandomRotation, RandomZoom, RandomContrast, RandomTranslation)
3. Preprocessing spesifik MobileNetV2 (skala [-1, 1])
4. Generator/Dataset pipeline menggunakan tf.data untuk performa tinggi tanpa data leakage
"""

import os
from typing import Tuple
import tensorflow as tf
from tensorflow.keras import layers

IMAGE_SIZE: Tuple[int, int] = (224, 224)
AUTOTUNE = tf.data.AUTOTUNE

def get_data_augmentation_layer() -> tf.keras.Sequential:
    """
    Membuat layer augmentasi citra yang realistis untuk buah-buahan.
    Augmentasi hanya diaplikasikan pada data training untuk mencegah overfitting.
    
    Penjelasan Akademis:
    - RandomFlip: Buah dapat dilihat dari berbagai orientasi horizontal & vertikal.
    - RandomRotation (15%): Simulasi sudut pengambilan foto buah yang bervariasi.
    - RandomZoom (10%): Simulasi jarak kamera yang sedikit berbeda.
    - RandomContrast (10%): Simulasi kondisi pencahayaan alami/ruangan.
    - RandomTranslation (8%): Variasi posisi buah dalam frame.
    """
    return tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical", name="aug_random_flip"),
        layers.RandomRotation(0.15, fill_mode="nearest", name="aug_random_rotation"),
        layers.RandomZoom(0.10, fill_mode="nearest", name="aug_random_zoom"),
        layers.RandomContrast(0.10, name="aug_random_contrast"),
        layers.RandomTranslation(height_factor=0.08, width_factor=0.08, fill_mode="nearest", name="aug_random_translation")
    ], name="data_augmentation")

def preprocess_image_path(filepath: str, label: int, is_training: bool = False) -> Tuple[tf.Tensor, tf.Tensor]:
    """
    Fungsi pemrosesan citra dari file path ke Tensor:
    1. Membaca file raw bytes
    2. Mendekode format citra (JPEG/PNG) ke RGB 3-channel
    3. Resize ke (224, 224)
    4. Menerapkan MobileNetV2 preprocess_input (skala rentang [-1, 1])
    """
    img_bytes = tf.io.read_file(filepath)
    # decode_image mendukung format JPEG, PNG, BMP, GIF
    img = tf.io.decode_image(img_bytes, channels=3, expand_animations=False)
    img = tf.image.resize(img, IMAGE_SIZE)
    img = tf.cast(img, tf.float32)
    img.set_shape([224, 224, 3])
    
    # Preprocessing spesifik MobileNetV2: memetakan pixel [0, 255] ke [-1, 1]
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    
    return img, label

def build_tf_dataset(df_split, batch_size: int = 32, is_training: bool = False, shuffle_buffer: int = 1000) -> tf.data.Dataset:
    """
    Membangun tf.data.Dataset dari pandas DataFrame (filepath dan label).
    Menggunakan caching, batching, dan prefetching untuk optimasi pipeline I/O.
    """
    filepaths = df_split['filepath'].values
    labels = df_split['label'].values
    
    dataset = tf.data.Dataset.from_tensor_slices((filepaths, labels))
    
    if is_training:
        dataset = dataset.shuffle(buffer_size=min(len(df_split), shuffle_buffer))
        
    dataset = dataset.map(
        lambda path, lbl: preprocess_image_path(path, lbl, is_training=is_training),
        num_parallel_calls=AUTOTUNE
    )
    
    dataset = dataset.batch(batch_size)
    
    if is_training:
        # Augmentasi diterapkan per-batch di GPU/CPU
        aug_layer = get_data_augmentation_layer()
        dataset = dataset.map(
            lambda x, y: (aug_layer(x, training=True), y),
            num_parallel_calls=AUTOTUNE
        )
        
    dataset = dataset.prefetch(buffer_size=AUTOTUNE)
    return dataset
