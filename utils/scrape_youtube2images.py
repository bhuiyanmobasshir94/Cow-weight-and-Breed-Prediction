import concurrent.futures
import glob
import os
import time

import cv2
import joblib
import pandas as pd
import yt_dlp
from tqdm import tqdm

from configs import *

details = glob.glob(f"{DATALAKE_DIR}/details/*.pkl")
data_list = []
for i, pkl in tqdm(enumerate(details), total=len(details)):
    data = joblib.load(pkl)
    data_list.append(data)
df = pd.DataFrame.from_dict(data_list, orient="columns")
df.to_csv(f"{DATALAKE_DIR}/pickles_to_df.csv", index=False)
df_sku_slug = df.loc[:, ["sku", "youtube_slug"]]

sku_slug_list = []
for index, row in df_sku_slug.iterrows():
    sku_slug_list.append((row["sku"], row["youtube_slug"]))

existed = 0
downloaded = 0


def apply_tuple(f):
    return lambda args: f(*args)


def sku2filename(sku):
    splitted_list = list(sku)
    file_name = "".join(splitted_list[:3]) + " " + "".join(splitted_list[3:]) + ".mp4"
    return file_name


@apply_tuple
def yt2imgs(sku, slug):
    if slug is None:
        print(f"Skipping {sku}: No YouTube slug available")
        return None

    url = f"https://www.youtube.com/watch?v={slug}"
    path = f"{DATALAKE_DIR}/yt_videos/{sku}"
    output_file = os.path.join(path, sku2filename(sku))

    # Create directory if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    # Check if video already exists
    if os.path.exists(output_file):
        global existed
        existed += 1
        print(f"Video for {sku} already exists at {output_file}")
        return None

    # Configure yt-dlp options
    ydl_opts = {
        "format": "best[ext=mp4]",  # Get the best mp4 format
        "outtmpl": output_file,  # Output file path
        "quiet": False,  # Show progress
        "no_warnings": False,  # Show warnings
        "ignoreerrors": True,  # Continue on error
        "no_color": True,  # No colors in output
        "progress_hooks": [
            lambda d: (
                print(f"\rDownloading: {d['_percent_str']}", end="")
                if d["status"] == "downloading"
                else None
            )
        ],
    }

    try:
        print(f"\nDownloading video for SKU: {sku}, YouTube ID: {slug}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Verify the file was downloaded
        if os.path.exists(output_file):
            global downloaded
            downloaded += 1
            print(f"\nSuccessfully downloaded video for {sku}")
            return True
        else:
            print(f"\nDownload reported success but file not found at {output_file}")
            return False
    except Exception as e:
        print(f"\nError downloading {url}: {type(e).__name__}: {e}")
        return False


t1 = time.perf_counter()

# Test with a single video first
if sku_slug_list:
    test_sku, test_slug = sku_slug_list[0]
    if test_slug is not None:
        print(f"Testing download with first video: {test_sku}, {test_slug}")
        result = yt2imgs((test_sku, test_slug))
        if result:
            print("Test download successful, continuing with remaining videos...")

            # Option 1: Process sequentially
            for args in sku_slug_list[1:]:
                sku, slug = args
                if slug is not None:
                    yt2imgs(args)

            # Option 2: Process in parallel (commented out)
            # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            #     executor.map(yt2imgs, [args for args in sku_slug_list[1:] if args[1] is not None])
        else:
            print(
                "Test download failed. Please check issues before processing all videos."
            )
    else:
        print("First item has no slug. Checking if others have slugs...")
        has_valid_slug = False
        for sku, slug in sku_slug_list:
            if slug is not None:
                has_valid_slug = True
                break
        if has_valid_slug:
            print("Found valid slugs in list. Processing videos...")
            for args in sku_slug_list:
                sku, slug = args
                if slug is not None:
                    yt2imgs(args)
        else:
            print("No valid YouTube slugs found in data. Check your data source.")
else:
    print("No SKU/slug pairs found. Check your data source.")

t2 = time.perf_counter()

print("========================================")
print(f"Finished in {t2-t1} seconds")
print(f"Total downloaded => {downloaded}")
print(f"Total existed => {existed}")
print("========================================")

yt_video_path_list = []
for dirname, _, filenames in os.walk(f"{DATALAKE_DIR}/yt_videos"):
    for filename in filenames:
        sku = dirname.split("/")[-1]
        yt_video_path_list.append((sku, f"{DATALAKE_DIR}/yt_videos/{sku}/{filename}"))

total_video_processed = 0


@apply_tuple
def video2images(sku, path, delay=0.4, min_image=25, max_image=30):
    cam = cv2.VideoCapture(path)
    output_path = f"{DATALAKE_DIR}/yt_images/{sku}"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if len(os.listdir(output_path)) > min_image:
        return

    fps = int(cam.get(cv2.CAP_PROP_FPS))
    currentframe = 0
    count = 0
    while True:
        ret, frame = cam.read()
        if ret:
            if currentframe == 0:
                currentframe += 1
                continue
            image_path = f"{DATALAKE_DIR}/yt_images/{sku}/{sku}_{count}.jpg"
            cv2.imwrite(image_path, frame)
            if cv2.imread(image_path) is None:
                os.remove(image_path)
            if count == max_image:
                break
            count += 1
            if delay:
                currentframe += delay * fps
                cam.set(1, currentframe)
        else:
            break
    global total_video_processed
    total_video_processed += 1
    cam.release()
    cv2.destroyAllWindows()
    print(f"Total images processed from this video => {count}, sku => {sku}")


t1 = time.perf_counter()

for args in yt_video_path_list:
    video2images(args)

t2 = time.perf_counter()

print("========================================")
print(f"Finished in {t2-t1} seconds")
print(f"Total videos processed => {total_video_processed}")
print("========================================")
