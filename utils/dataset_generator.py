from utils.configs import *
from utils.aws_wrappers import *
import pandas as pd
import glob
import boto3

s3 = boto3.resource(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def run_command(command=["ls", "-l"]):
    import subprocess

    # Execute a system command
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Check if the command was successful
    if result.returncode == 0:
        print("Command executed successfully")
        print("Output:")
        print(result.stdout)
    else:
        print("Error executing command:")
        print(result.stderr)


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
        # print(f"Loading percentage ", index + 1 / len(df_csv), "%")
        sku = row["sku"]
        images = glob.glob(f"{yearly_dir}/images/{sku}/*.jpg")
        run_command(
            command=[
                "aws",
                "s3",
                "cp",
                "--recursive",
                f"{yearly_dir}/images/{sku}",
                f"s3://{S3_BUCKET_NAME}/images/{sku}",
            ]
        )
        # for img in images:
        #     name = img.split("/")[-1]
        #     s3.Bucket(S3_BUCKET_NAME).upload_file(img, f"images/{sku}/{name}")
        HD_IMAGES_COUNT += len(images)
        videos = glob.glob(f"{yearly_dir}/yt_videos/{sku}/*.mp4")
        run_command(
            command=[
                "aws",
                "s3",
                "cp",
                "--recursive",
                f"{yearly_dir}/yt_videos/{sku}",
                f"s3://{S3_BUCKET_NAME}/videos/{sku}",
            ]
        )
        # for video in videos:
        #     name = video.split("/")[-1]
        #     s3.Bucket(S3_BUCKET_NAME).upload_file(video, f"videos/{sku}/{name}")
        YOUTUBE_VIDEOS_COUNT += len(videos)

DF.to_csv(f"{BASE_DIR}/cow_dataset.csv", index=False)
run_command(
    command=[
        "aws",
        "s3",
        "cp",
        "--recursive",
        f"{BASE_DIR}/cow_dataset.csv",
        f"s3://{S3_BUCKET_NAME}/data/cow_dataset_{TOTAL_DATA_COUNT}.csv",
    ]
)
# s3.Bucket(S3_BUCKET_NAME).upload_file(
#     f"{BASE_DIR}/cow_dataset.csv", f"data/cow_dataset_{TOTAL_DATA_COUNT}.csv"
# )

print("Total Cow Data Count => ", TOTAL_DATA_COUNT)
print("Total Cow HD Images => ", HD_IMAGES_COUNT)
print("Total Cow Youtube Videos Count => ", YOUTUBE_VIDEOS_COUNT)
print("Final Cow Data Count => ", len(DF))
