from utils.configs import *
from utils.aws_wrappers import *
import pandas as pd
import glob
import boto3
import re

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
    # if result.returncode == 0:
    #     print("Command executed successfully")
    #     print("Output:")
    #     print(result.stdout)
    # else:
    #     print("Error executing command:")
    #     print(result.stderr)

    return result


import os


def rename_folders(root_dir):
    for root, dirs, files in os.walk(root_dir, topdown=False):
        for name in dirs:
            current_dir = os.path.join(root, name)
            new_name = name.replace(
                " ", ""
            )  # Replace "old_string" with the string you want to replace and "new_string" with the new string
            if name != new_name:
                new_dir = os.path.join(root, new_name)
                os.rename(current_dir, new_dir)
                print(f"Renamed directory: {current_dir} -> {new_dir}")


dataset_dirs = ["data-2021", "data-2022", "data-2023"]
HD_IMAGES_COUNT = 0
YOUTUBE_VIDEOS_COUNT = 0
TOTAL_DATA_COUNT = 0
DF = None

for dir in dataset_dirs:
    yearly_dir = BASE_DIR + "/" + dir
    rename_folders(f"{yearly_dir}/images/")
    rename_folders(f"{yearly_dir}/yt_videos/")
    df_csv = pd.read_csv(os.path.join(yearly_dir, "pickles_to_df.csv"))
    df_csv["sku"] = df_csv["sku"].str.replace(" ", "")
    if DF is not None:
        DF = pd.concat([DF, df_csv], axis=0)
    else:
        DF = df_csv
    TOTAL_DATA_COUNT += len(df_csv)
    for index, row in df_csv.iterrows():
        sku = row["sku"]
        images = glob.glob(f"{yearly_dir}/images/{sku}/*.jpg")
        result = run_command(
            command=[
                "aws",
                "s3",
                "ls",
                f"s3://{S3_BUCKET_NAME}/images/{sku}/",
                "--human-readable",
                "--summarize",
            ]
        )
        pattern = r"Total Objects: (\d+)"
        match = re.search(pattern, result.stdout)
        if match:
            count = match.group(1)
            if len(images) != int(count):
                print(f"Folder has {len(images)}, found {count} for {sku}")
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
        HD_IMAGES_COUNT += len(images)
        videos = glob.glob(f"{yearly_dir}/yt_videos/{sku}/*.mp4")
        result = run_command(
            command=[
                "aws",
                "s3",
                "ls",
                f"s3://{S3_BUCKET_NAME}/videos/{sku}/",
                "--human-readable",
                "--summarize",
            ]
        )
        pattern = r"Total Objects: (\d+)"
        match = re.search(pattern, result.stdout)
        if match:
            count = match.group(1)
            if len(videos) != int(count):
                print(f"Folder has {len(videos)}, found {count} for {sku}")
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
        YOUTUBE_VIDEOS_COUNT += len(videos)

DF.to_csv(f"{BASE_DIR}/cow_dataset.csv", index=False)
run_command(
    command=[
        "aws",
        "s3",
        "cp",
        f"{BASE_DIR}/cow_dataset.csv",
        f"s3://{S3_BUCKET_NAME}/data/cow_dataset_{TOTAL_DATA_COUNT}.csv",
    ]
)
with open(f"{BASE_DIR}/note.txt", "w") as file:
    file.writelines(f"Total Cow Data Count => {TOTAL_DATA_COUNT} \n")
    file.writelines(f"Total Cow HD Images => {HD_IMAGES_COUNT} \n")
    file.writelines(f"Total Cow Youtube Videos Count => {YOUTUBE_VIDEOS_COUNT} \n")
    file.writelines(f"Final Cow Data Count => {len(DF)} \n")

run_command(
    command=[
        "aws",
        "s3",
        "cp",
        f"{BASE_DIR}/note.txt",
        f"s3://{S3_BUCKET_NAME}/data/note.txt",
    ]
)
