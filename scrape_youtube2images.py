import pandas as pd
import joblib
import os
import time
import concurrent.futures
import glob
from tqdm import tqdm
from pytube import YouTube
import cv2
import time

details = glob.glob("details/*.pkl")
data_list = []
for i, pkl in tqdm(enumerate(details), total=len(details)):
    data = joblib.load(pkl)
    data_list.append(data)
df = pd.DataFrame.from_dict(data_list, orient="columns")
df.to_csv("data/pickles_to_df.csv", index=False)
df_sku_slug = df.loc[:, ["sku", "youtube_slug"]]

sku_slug_list = []
for index, row in df_sku_slug.iterrows():
    sku_slug_list.append((row["sku"], row["youtube_slug"]))

existed = 0
downloaded = 0

apply_tuple = lambda f: lambda args: f(*args)


def sku2filename(sku):
    splitted_list = list(sku)
    file_name = "".join(splitted_list[:3]) + " " + "".join(splitted_list[3:]) + ".mp4"
    return file_name


@apply_tuple
def yt2imgs(sku, slug):
    url = f"https://www.youtube.com/watch?v={slug}"
    path = f"yt_videos/{sku}"
    if not os.path.exists(path):
        os.mkdir(path)
    if len(os.listdir(path)) == 1 and os.listdir(path)[0] == sku2filename(sku):
        global existed
        existed += 1
        return None
    try:
        YouTube(url).streams.filter(progressive=True, file_extension="mp4").order_by(
            "resolution"
        ).desc().first().download(path)
        global downloaded
        downloaded += 1
    except Exception as e:
        print(f"Got exception for {url}, exception: {e}")


t1 = time.perf_counter()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     executor.map(yt2imgs, sku_slug_list)

for args in sku_slug_list:
    yt2imgs(args)

t2 = time.perf_counter()

print("========================================")
print(f"Finished in {t2-t1} seconds")
print(f"Total downloaded => {downloaded}")
print(f"Total existed => {existed}")
print("========================================")

yt_video_path_list = []
for dirname, _, filenames in os.walk("yt_videos"):
    for filename in filenames:
        sku = dirname.split("\\")[1]
        yt_video_path_list.append((sku, f"yt_videos/{sku}/{filename}"))

total_video_processed = 0


@apply_tuple
def video2images(sku, path, delay=0.4, min_image=25, max_image=30):
    cam = cv2.VideoCapture(path)
    output_path = f"yt_images/{sku}"
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
            image_path = f"yt_images/{sku}/{sku}_{count}.jpg"
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
