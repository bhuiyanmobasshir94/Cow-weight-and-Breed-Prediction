import glob
import os
import sys

import pandas as pd

from aws_wrappers import S3
from configs import *
from extractor import make_tar

s3 = S3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

file_name = os.path.join(DATALAKE_DIR, "pickles_to_df.csv")
out_file_name = os.path.join(DATALAKE_DIR, "dataset.csv")
columns = ['sku', 'sex', 'color', 'breed', 'feed', 'age_in_month',
           'teeth', 'height_in_inch', 'weight_in_kg', 'price', 'size']

null_yt_images_count = 0
null_yt_videos_count = 0
null_images_count = 0
null_pkl_count = 0
exists_for_all = 0

if not os.path.exists(file_name):
    logger.warning("Pickles to df file not found")
    sys.exit(1)
else:
    df = pd.read_csv(file_name, usecols=columns)
    df['images_count'] = 0
    df['yt_images_count'] = 0
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
            else:
                df.loc[index, 'images_count'] = len(
                    glob.glob(f"{images_path}/*.jpg"))
            if not os.path.exists(yt_images_path) or (os.path.exists(yt_images_path) and len(glob.glob(f"{yt_images_path}/*.jpg")) == 0):
                logger.info("Folder %s doesn't exist for yt_images",
                            row["sku"])
                null_yt_images_count += 1
            else:
                df.loc[index, 'yt_images_count'] = len(
                    glob.glob(f"{yt_images_path}/*.jpg"))
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
    # logger.info(f"Columns: {df.columns.values}")
    df['total_images'] = df['images_count'] + df['yt_images_count']
    df.rename(columns={'age_in_month': 'age_in_year'}, inplace=True)
    df.age_in_year = df.age_in_year.apply(lambda x: x.split(" ")[0])
    df.loc[231, "weight_in_kg"] = 185
    df.loc[97, "weight_in_kg"] = 190
    df.loc[486, "weight_in_kg"] = 192
    df.loc[335, "size"] = "MINIMUM"
    df.loc[373, "size"] = "EXTRA_LARGE"
    df.drop([334], inplace=True)
    df.to_csv(out_file_name, index=False)
    gz_path = make_tar(out_file_name)
    base_name = os.path.basename(gz_path)
    data = open(gz_path, 'rb')
    s3.put_object_to_s3(data, "cv-datasets-2021", None, base_name)
    logger.info(df.head())
    logger.info("Loaded the dataframe")
    logger.info("Dataframe shape => %s", df.shape)

logger.warning("Null yt images count => %s", null_yt_images_count)
logger.warning("Null images count => %s", null_images_count)
logger.warning("Null yt videos count => %s", null_yt_videos_count)
logger.warning("Null pickles count => %s", null_pkl_count)
logger.info("Exists for all count => %s", exists_for_all)
