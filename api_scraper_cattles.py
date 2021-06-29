import requests
import joblib
import os
import json
from collections import defaultdict
from datetime import datetime


DATA_DICT_LIST = []


def scrape(url):
    response = requests.get(url).content
    json_response = json.loads(response)
    return json_response


def download_image(img_url, img_name):
    img_bytes = requests.get(img_url).content
    with open(img_name, "wb") as img_file:
        img_file.write(img_bytes)
        print(f"{img_name} was downloaded...")


def all_cattles():
    url = "https://admin.bengalmeat.com/api/cattle/"
    json_response = scrape(url)
    if json_response["status"] is True:
        data_count = json_response["data"]["count"] + 1
        for offset in range(0, data_count, 20):
            url = f"https://admin.bengalmeat.com/api/cattle/?limit=20&offset={offset}"
            json_response = scrape(url)
            DATA_DICT_LIST.extend(json_response["data"]["results"])
    assert (data_count - 1) == len(DATA_DICT_LIST)
    print("========================================")
    print("Data count => ", json_response["data"]["count"])
    print("Downloaded data count => ", len(DATA_DICT_LIST))
    print("========================================")


all_cattles()


ext = str(datetime.today().date()).replace("-", "_")


joblib.dump(DATA_DICT_LIST, f"pickles/DATA_DICT_LIST_{ext}.pkl")
print("Dumped data dict list")

IMAGES_DICT = defaultdict(list)
for value in DATA_DICT_LIST:
    IMAGES_DICT[value["sku"]].append(value["thumbnail"])
    for slide in value["slides"]:
        IMAGES_DICT[value["sku"]].append(slide["image"])


joblib.dump(IMAGES_DICT, f"pickles/IMAGES_DICT_{ext}.pkl")
print("Dumped images dict")


IMAGES_DICT = dict(IMAGES_DICT)

for key, value in IMAGES_DICT.items():
    if os.path.exists(f"images/{key}"):
        for index, img_url in enumerate(value):
            img_name = f"images/{key}/{key}_{index}.jpg"
            if not os.path.exists(img_name):
                download_image(img_url, img_name)
    else:
        os.mkdir(f"images/{key}")
        for index, img_url in enumerate(value):
            img_name = f"images/{key}/{key}_{index}.jpg"
            if not os.path.exists(img_name):
                download_image(img_url, img_name)


image_count = 0
dir_count = 0
for dirname, _, filenames in os.walk("images"):
    # print(dirname)
    # print(filenames)
    if os.path.exists(dirname) and dirname is not "images":
        dir_count += 1
    for filename in filenames:
        if os.path.exists(os.path.join(dirname, filename)):
            image_count += 1

print("========================================")
print("Total images scraped => ", image_count)
print("Total cow scraped => ", dir_count)
print("========================================")

DATA_DICT_LIST = joblib.load(f"pickles/DATA_DICT_LIST_{ext}.pkl")
print("Loaded data dict list")
IMAGES_DICT = joblib.load(f"pickles/IMAGES_DICT_{ext}.pkl")
print("Loaded images dict")

if os.path.exists("pickles/FINAL_DATA_DICT.pkl"):
    FINAL_DATA_DICT = joblib.load("pickles/FINAL_DATA_DICT.pkl")
    print("Loaded final data dict")
else:
    FINAL_DATA_DICT = defaultdict(dict)
    print("Defined default final data dict")
for value in DATA_DICT_LIST:
    value["images_list"] = IMAGES_DICT[value["sku"]]
    FINAL_DATA_DICT[value["sku"]] = dict(value)

joblib.dump(FINAL_DATA_DICT, "pickles/FINAL_DATA_DICT.pkl")
print("Dumped final data dict")

print("========================================")
print("Final data dict total count => ", len(FINAL_DATA_DICT.keys()))
print("========================================")

shutdown = input("\n Do you want me to end? Press y to proceed.\n >>> ")
