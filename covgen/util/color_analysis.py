import base64
from io import BytesIO

import numpy as np
from sklearn.cluster import KMeans
from PIL import Image


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
    return center_colors[max_weighted_index].astype(np.int8)
