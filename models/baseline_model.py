import glob
import os
import time

import matplotlib
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath("__file__")))
DATA_DIR = os.path.join(PARENT_DIR, "data")
DATASET = os.path.join(DATA_DIR, "dataset.csv")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
YT_IMAGES_DIR = os.path.join(DATA_DIR, "yt_images")
images = glob.glob(f"{IMAGES_DIR}/*/*.jpg")
yt_images = glob.glob(f"{YT_IMAGES_DIR}/*/*.jpg")

df = pd.read_csv(DATASET)

image = tf.keras.preprocessing.image.load_img(images[0])
input_arr = tf.keras.preprocessing.image.img_to_array(image)
input_arr = np.array([input_arr])  # Convert single image to a batch.
print(input_arr)
