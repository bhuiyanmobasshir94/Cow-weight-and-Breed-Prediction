from utils.configs import *

import pandas as pd
import glob

dataset_dirs = ["data-2021", "data-2022", "data-2023"]
HD_IMAGES_COUNT = 0
YOUTUBE_VIDEOS_COUNT = 0
TOTAL_DATA_COUNT = 0

for dir in dataset_dirs:
    yearly_dir = BASE_DIR + "/" + dir
    df_csv = pd.read_csv(os.path.join(yearly_dir, "pickles_to_df.csv"))
    TOTAL_DATA_COUNT += len(df_csv)
    for index, row in df_csv.iterrows():
        sku = row["sku"]
        images = glob.glob(f"{yearly_dir}/images/{sku}/*.jpg")
        HD_IMAGES_COUNT += len(images)
        videos = glob.glob(f"{yearly_dir}/yt_videos/{sku}/*.mp4")
        YOUTUBE_VIDEOS_COUNT += len(videos)


print("Total Data Count => ", TOTAL_DATA_COUNT)
print("Total HD Images => ", HD_IMAGES_COUNT)
print("Total Youtube Videos Count => ", YOUTUBE_VIDEOS_COUNT)
