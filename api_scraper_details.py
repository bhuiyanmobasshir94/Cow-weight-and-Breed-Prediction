import joblib
import os
import requests
import json
import concurrent.futures
import time

apply_tuple = lambda f: lambda args: f(*args)


def scrape_detail(id):
    url = f"https://admin.bengalmeat.com/api/cattle/{str(id)}/detail"
    response = requests.get(url).content
    json_response = json.loads(response)
    return json_response


data_dict = dict(joblib.load("pickles/FINAL_DATA_DICT.pkl"))

id_sku_list = []
for value in data_dict.values():
    id_sku_list.append((value["id"], value["sku"]))

count = 0
already_exists = 0


@apply_tuple
def download_detail(id, sku):
    path = f"details/{sku}.pkl"
    if os.path.exists(path):
        global already_exists
        already_exists += 1
    else:
        response = scrape_detail(id)
        if response["status"] is True and response.get("data", None) is not None:
            data = dict(response["data"])
            joblib.dump(data, path)
            global count
            count += 1
    return None


t1 = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(download_detail, id_sku_list)

t2 = time.perf_counter()

print("========================================")
print(f"total downloaded => {count}")
print(f"total skipped => {already_exists}")
print(f"Finished in {t2-t1} seconds")
print("========================================")

shutdown = input("\n Do you want me to end? Press y to proceed.\n >>> ")


# data = joblib.load("pickles/FINAL_DATA_DICT.pkl")
# data_dict = dict(data)
# data_list = []
# for value in data_dict.values():
#     data_list.append(value)

# count = 0
# already_exists = 0
# for index, value in enumerate(data_list):
#     response = scrape_detail(value["id"])
#     if response["status"] is True and response.get("data", None) is not None:
#         data = dict(response["data"])
#         sku = data["sku"]
#         path = f"details/{sku}.pkl"
#         if not os.path.exists(path):
#             print(f"Downloading sku: {sku}...")
#             joblib.dump(data, path)
#             count += 1
#         else:
#             already_exists += 1

# print("========================================")
# print(f"total downloaded => {count}")
# print(f"total skipped => {already_exists}")
# print("========================================")
