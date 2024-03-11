from utils.configs import *

import pandas as pd
import glob

dataset_dirs = ["data-2021", "data-2022", "data-2023"]
HD_IMAGES_COUNT = 0
YOUTUBE_VIDEOS_COUNT = 0
TOTAL_DATA_COUNT = 0
DF = None

for dir in dataset_dirs:
    yearly_dir = BASE_DIR + "/" + dir
    df_csv = pd.read_csv(os.path.join(yearly_dir, "pickles_to_df.csv"))
    if DF is not None:
        DF = pd.concat([DF, df_csv], axis=0)
    else:
        DF = df_csv
    TOTAL_DATA_COUNT += len(df_csv)
    for index, row in df_csv.iterrows():
        sku = row["sku"]
        images = glob.glob(f"{yearly_dir}/images/{sku}/*.jpg")
        HD_IMAGES_COUNT += len(images)
        videos = glob.glob(f"{yearly_dir}/yt_videos/{sku}/*.mp4")
        YOUTUBE_VIDEOS_COUNT += len(videos)


print("Total Cow Data Count => ", TOTAL_DATA_COUNT)
print("Total Cow HD Images => ", HD_IMAGES_COUNT)
print("Total Cow Youtube Videos Count => ", YOUTUBE_VIDEOS_COUNT)
print("Final Cow Data Count => ", len(DF))
