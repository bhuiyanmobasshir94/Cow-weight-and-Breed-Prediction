import glob
import os
import sys

import pandas as pd
from genericpath import exists

from configs import *

file_name = os.path.join(DATALAKE_DIR, "pickles_to_df.csv")

null_yt_images_count = 0
null_yt_videos_count = 0
null_images_count = 0
null_pkl_count = 0
exists_for_all = 0

if not os.path.exists(file_name):
    logger.warning("Pickles to df file not found")
    sys.exit(1)
else:
    df = pd.read_csv(file_name)
    logger.info("Loaded the dataframe")
    logger.info("Dataframe shape => %s", df.shape)
    for index, row in df.iterrows():
        images_path = os.path.join(IMAGES_DIR, row["sku"])
        yt_images_path = os.path.join(YT_IMAGES_DIR, row["sku"])
        yt_videos_path = os.path.join(YT_VIDEOS_DIR, row["sku"])
        pickle_path = os.path.join(DETAILS_DIR, f"{row['sku']}.pkl")

        if os.path.exists(images_path) or os.path.exists(yt_images_path) or os.path.exists(yt_videos_path) or os.path.exists(pickle_path):
            if not os.path.exists(images_path) or (os.path.exists(images_path) and len(glob.glob(f"{images_path}/*.jpg")) == 0):
                logger.info("Folder %s doesn't exist for images",
                            row["sku"])
                null_images_count += 1
            if not os.path.exists(yt_images_path) or (os.path.exists(yt_images_path) and len(glob.glob(f"{yt_images_path}/*.jpg")) == 0):
                logger.info("Folder %s doesn't exist for yt_images",
                            row["sku"])
                null_yt_images_count += 1
            if not os.path.exists(yt_videos_path) or (os.path.exists(yt_videos_path) and len(glob.glob(f"{yt_videos_path}/*.mp4")) == 0):
                logger.info("Folder %s doesn't exist for yt_videos",
                            row["sku"])
                null_yt_videos_count += 1
            if not os.path.exists(pickle_path):
                logger.info("Pickle file %s doesn't exist",
                            row["sku"])
                null_pkl_count += 1
            if (os.path.exists(images_path) and os.path.exists(yt_images_path) and os.path.exists(yt_videos_path) and os.path.exists(pickle_path)) and (len(glob.glob(f"{images_path}/*.jpg")) > 0 and len(glob.glob(f"{yt_images_path}/*.jpg")) > 0 and len(glob.glob(f"{yt_videos_path}/*.mp4")) > 0):
                exists_for_all += 1
        else:
            logger.info("Folder %s doesn't exist", row["sku"])

logger.warning("Null yt images count => %s", null_yt_images_count)
logger.warning("Null images count => %s", null_images_count)
logger.warning("Null yt videos count => %s", null_yt_videos_count)
logger.warning("Null pickles count => %s", null_pkl_count)
logger.info("Exists for all count => %s", exists_for_all)
