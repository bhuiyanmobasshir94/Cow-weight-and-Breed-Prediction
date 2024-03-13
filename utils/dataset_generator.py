from utils.configs import *
from utils.aws_wrappers import *
import pandas as pd
import glob

s3 = S3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

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
        print(f"Loading percentage ", index + 1 / len(df_csv), "%")
        sku = row["sku"]
        images = glob.glob(f"{yearly_dir}/images/{sku}/*.jpg")
        for img in images:
            data = open(img, "rb")
            name = img.split("/")[-1]
            # s3.put_object_to_s3(data, S3_BUCKET_NAME, f"images/{sku}", name)
        HD_IMAGES_COUNT += len(images)
        videos = glob.glob(f"{yearly_dir}/yt_videos/{sku}/*.mp4")
        for video in videos:
            data = open(video, "rb")
            name = video.split("/")[-1]
            # s3.put_object_to_s3(data, S3_BUCKET_NAME, f"videos/{sku}", name)
        YOUTUBE_VIDEOS_COUNT += len(videos)

DF.to_csv(f"{BASE_DIR}/cow_dataset.csv", index=False)
data = open(f"{BASE_DIR}/cow_dataset.csv", "rb")
s3.put_object_to_s3(data, S3_BUCKET_NAME, "data", "cow_dataset.csv")

print("Total Cow Data Count => ", TOTAL_DATA_COUNT)
print("Total Cow HD Images => ", HD_IMAGES_COUNT)
print("Total Cow Youtube Videos Count => ", YOUTUBE_VIDEOS_COUNT)
print("Final Cow Data Count => ", len(DF))
