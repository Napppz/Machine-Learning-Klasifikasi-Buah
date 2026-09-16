"""
Module gradcam.py
Explainable AI (XAI) - Gradient-weighted Class Activation Mapping (Grad-CAM)
Memvisualisasikan area piksel mana dari citra buah yang paling memengaruhi keputusan model MobileNetV2.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image
import tensorflow as tf
from typing import Tuple, Optional

from src.preprocessing import IMAGE_SIZE

def generate_gradcam_heatmap(img_array: np.ndarray, model: tf.keras.Model, pred_index: Optional[int] = None) -> np.ndarray:
    """
    Menghitung Grad-CAM Heatmap untuk arsitektur Transfer Learning MobileNetV2.
    img_array: float32 array dengan shape (1, 224, 224, 3) yang sudah dipreprocess.
    """
    base_model = None
    for layer in model.layers:
        if "mobilenetv2" in layer.name.lower():
            base_model = layer
            break
            
    if base_model is None:
        raise ValueError("Layer MobileNetV2 tidak ditemukan di dalam model.")
        
    last_conv_layer = base_model.get_layer("out_relu")
    
    # Model ekstraksi konvolusi dan output base model
    grad_base = tf.keras.Model(base_model.inputs, [last_conv_layer.output, base_model.output])
    
    # Rekonstruksi top head model
    head_input = tf.keras.Input(shape=base_model.output.shape[1:])
    x = head_input
    for layer in model.layers[2:]:
        x = layer(x)
    head_model = tf.keras.Model(head_input, x)
    
    with tf.GradientTape() as tape:
        conv_outputs, base_out = grad_base(img_array)
        tape.watch(conv_outputs)
        preds = head_model(base_out)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        loss = preds[:, pred_index]
        
    # Gradien output prediksi terhadap feature map layer konvolusi terakhir
    grads = tape.gradient(loss, conv_outputs)
    
    # Global Average Pooling dari gradien (bobot pentingnya masing-masing channel)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    
    # Kalikan feature map dengan bobot gradien dan jumlahkan antar-channel
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs[0]), axis=-1)
    
    # Terapkan ReLU agar hanya fitur yang berkontribusi positif yang dipertahankan
    heatmap = np.maximum(heatmap, 0)
    
    max_val = np.max(heatmap)
    if max_val > 0:
        heatmap /= max_val
        
    return heatmap

def create_gradcam_overlay(original_pil_img: Image.Image, heatmap: np.ndarray, alpha: float = 0.4) -> Image.Image:
    """
    Menggabungkan heatmap Grad-CAM berwarna JET di atas citra asli.
    """
    img_resized = original_pil_img.resize(IMAGE_SIZE)
    img_np = np.array(img_resized)
    
    # Resize heatmap dari 7x7 ke 224x224
    heatmap_pil = Image.fromarray(np.uint8(255 * heatmap)).resize(IMAGE_SIZE, Image.Resampling.BILINEAR)
    heatmap_np = np.array(heatmap_pil) / 255.0
    
    # Konversi heatmap ke colormap JET (RGB)
    jet = plt.colormaps["jet"]
    jet_colors = jet(heatmap_np)[:, :, :3]
    jet_heatmap = np.uint8(255 * jet_colors)
    
    # Blending antara citra asli dan heatmap
    overlay_np = np.uint8((1.0 - alpha) * img_np + alpha * jet_heatmap)
    return Image.fromarray(overlay_np)
