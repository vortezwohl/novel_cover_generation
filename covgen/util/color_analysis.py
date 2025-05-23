import base64
from io import BytesIO

import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import matplotlib.colors as mcolors


def find_dominant_color(b64_image: str, n_colors: int = 1) -> np.ndarray:
    img = Image.open(fp=BytesIO(base64.b64decode(b64_image))).convert('RGB')
    img_array = np.array(img)
    h, w, _ = img_array.shape
    img_array = img_array.reshape((h * w, 3))
    kmeans = KMeans(n_clusters=n_colors, random_state=0)
    kmeans.fit(img_array)
    center_colors = kmeans.cluster_centers_
    labels = kmeans.labels_
    color_weights = np.bitwise_count(labels) / len(labels)
    max_weighted_index = np.argmax(color_weights)
    return np.maximum(center_colors[max_weighted_index], 0.).astype(np.int8)


def find_contrast_color(rgb_color: np.ndarray) -> np.ndarray:
    hsv = mcolors.rgb_to_hsv(rgb_color / 255.0)
    contrast_hsv = hsv.copy()
    contrast_hsv[0] = (hsv[0] + 0.5) % 1.0
    contrast_color = mcolors.hsv_to_rgb(contrast_hsv) * 255
    return np.maximum(contrast_color, 0.).astype(np.int8)
