import json
import os
from collections import defaultdict
from datetime import datetime

import joblib
import requests

from configs import *

DATA_DICT_LIST = []
ext = str(datetime.today().date()).replace("-", "_")
IMAGES_DICT = defaultdict(list)


def scrape(url):
    response = requests.get(url).content
    json_response = json.loads(response)
    return json_response


def download_image(img_url, img_name):
    img_bytes = requests.get(img_url).content
    with open(img_name, "wb") as img_file:
        img_file.write(img_bytes)
        logger.info(f"{img_name} was downloaded...")


def all_cattles():
    # url = "https://admin.bengalmeat.com/api/cattle/"
    url = DATA_VENDOR_URL
    json_response = scrape(url)
    if json_response["status"] is True:
        data_count = json_response["data"]["count"] + 1
        for offset in range(0, data_count, 20):
            url = f"{url}?limit=20&offset={offset}"
            json_response = scrape(url)
            DATA_DICT_LIST.extend(json_response["data"]["results"])
    assert (data_count - 1) == len(DATA_DICT_LIST)
    logger.info("========================================")
    logger.info(f"Data count => %s",
                json_response["data"]["count"], exc_info=1)
    logger.info("Downloaded data count => %s", len(DATA_DICT_LIST), exc_info=1)
    logger.info("========================================")


def dump_data_dict():
    joblib.dump(DATA_DICT_LIST,
                f"{DATALAKE_DIR}/pickles/DATA_DICT_LIST_{ext}.pkl")
    logger.info("Dumped data dict list")


def dump_images_dict():
    for value in DATA_DICT_LIST:
        IMAGES_DICT[value["sku"]].append(value["thumbnail"])
        for slide in value["slides"]:
            IMAGES_DICT[value["sku"]].append(slide["image"])
    logger.info("Downloaded images dict count => %s", len(IMAGES_DICT), exc_info=1)
    joblib.dump(IMAGES_DICT, f"{DATALAKE_DIR}/pickles/IMAGES_DICT_{ext}.pkl")
    logger.info("Dumped images dict")


def download_images():
    # IMAGES_DICT = dict(IMAGES_DICT)
    IMAGES_DICT = joblib.load(f"{DATALAKE_DIR}/pickles/IMAGES_DICT_{ext}.pkl")
    for key, value in IMAGES_DICT.items():
        if os.path.exists(f"{DATALAKE_DIR}/images/{key}"):
            for index, img_url in enumerate(value):
                img_name = f"{DATALAKE_DIR}/images/{key}/{key}_{index}.jpg"
                if not os.path.exists(img_name):
                    download_image(img_url, img_name)
        else:
            os.mkdir(f"{DATALAKE_DIR}/images/{key}")
            for index, img_url in enumerate(value):
                img_name = f"{DATALAKE_DIR}/images/{key}/{key}_{index}.jpg"
                if not os.path.exists(img_name):
                    download_image(img_url, img_name)


def scrape_report():
    image_count = 0
    dir_count = 0
    for dirname, _, filenames in os.walk(f"{DATALAKE_DIR}/images"):
        # print(dirname)
        # print(filenames)
        if os.path.exists(dirname) and dirname != "images":
            dir_count += 1
        for filename in filenames:
            if os.path.exists(os.path.join(dirname, filename)):
                image_count += 1

    logger.info("========================================")
    logger.info("Total images scraped => %s", image_count, exc_info=1)
    logger.info("Total cow scraped => %s", dir_count, exc_info=1)
    logger.info("========================================")


def update_final_dict():
    DATA_DICT_LIST = joblib.load(
        f"{DATALAKE_DIR}/pickles/DATA_DICT_LIST_{ext}.pkl")
    logger.info("Loaded data dict list")
    IMAGES_DICT = joblib.load(f"{DATALAKE_DIR}/pickles/IMAGES_DICT_{ext}.pkl")
    logger.info("Loaded images dict")

    if os.path.exists(f"{DATALAKE_DIR}/pickles/FINAL_DATA_DICT.pkl"):
        FINAL_DATA_DICT = joblib.load(
            f"{DATALAKE_DIR}/pickles/FINAL_DATA_DICT.pkl")
        logger.info("Loaded final data dict")
    else:
        FINAL_DATA_DICT = defaultdict(dict)
        logger.info("Defined default final data dict")
    for value in DATA_DICT_LIST:
        value["images_list"] = IMAGES_DICT[value["sku"]]
        FINAL_DATA_DICT[value["sku"]] = dict(value)

    joblib.dump(FINAL_DATA_DICT, f"{DATALAKE_DIR}/pickles/FINAL_DATA_DICT.pkl")
    logger.info("Dumped final data dict")

    logger.info("========================================")
    logger.info("Final data dict total count => %s",
                len(FINAL_DATA_DICT.keys()), exc_info=1)
    logger.info("========================================")


# print("Shout out from detail scraper >>>")

# print("Shout out from youtube videos to images scraper >>>")
# print("========================================")

# print("Shout out from analytics >>>")

# shutdown = input("\n Do you want me to end? Press y to proceed.\n >>> ")

if __name__ == "__main__":
    all_cattles()
    dump_data_dict()
    dump_images_dict()
    download_images()
    scrape_report()
    update_final_dict()
    import api_scraper_details
    import scrape_youtube2images
    import analytics
