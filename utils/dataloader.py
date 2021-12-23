import glob
import os
import sys

import pandas as pd

from configs import *
from utilities import *

columns = ['sku', 'type', 'sex', 'color', 'breed', 'age_in_month',
           'height_in_inch', 'weight_in_kg', 'price', 'size', 'images_count', 'yt_images_count']

if not os.path.exists(DATASET_FILE_PATH):
    logger.warning("Dataset file not found")
    logger.info("Downloading dataset, it may take 1 to 2 minutes")
    download(DATASET_URL, DATASET_FILE_PATH)

if not len(glob.glob(f"{IMAGES_DIR}/*")) > 0:
    logger.warning("Images not found")
    logger.info("Downloading images, it may take 12 to 15 minutes")
    download(IMAGES_URL, str(IMAGES_DIR))

if not len(glob.glob(f"{YT_IMAGES_DIR}/*")) > 0:
    logger.warning("YT images not found")
    logger.info("Downloading yt_images, it may take 85 to 90 minutes")
    download(YT_IMAGES_URL, str(YT_IMAGES_DIR))

df = pd.read_csv(DATASET_FILE_PATH, usecols=columns)
logger.info(df.head())
for index, row in df.iterrows():
    images_path = os.path.join(IMAGES_DIR, row["sku"])
    yt_images_path = os.path.join(YT_IMAGES_DIR, row["sku"])
    all_images = []
    if row['images_count'] > 0:
        all_images.extend(glob.glob(f"{images_path}/*.jpg"))
    if row['yt_images_count'] > 0:
        all_images.extend(glob.glob(f"{yt_images_path}/*.jpg"))
    logger.info(f"{row['sku']} has {len(all_images)} images")
    for images in all_images:
        logger.info(images)
