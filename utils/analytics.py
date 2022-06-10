import glob
import os

from configs import *


def get_size(start_path="."):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def bytes_to_unit(bytes, unit):
    mapper = {
        "B": "{:,.2f}".format(bytes) + " B",
        "kb": "{:,.2f}".format(bytes / float(1 << 7)) + " kb",
        "KB": "{:,.2f}".format(bytes / float(1 << 10)) + " KB",
        "mb": "{:,.2f}".format(bytes / float(1 << 17)) + " mb",
        "MB": "{:,.2f}".format(bytes / float(1 << 20)) + " MB",
        "gb": "{:,.2f}".format(bytes / float(1 << 27)) + " gb",
        "GB": "{:,.2f}".format(bytes / float(1 << 30)) + " GB",
        "TB": "{:,.2f}".format(bytes / float(1 << 40)) + " TB",
    }
    key = str(unit.strip())
    value = mapper.get(key, None)
    if value:
        return mapper[key]
    else:
        raise NotImplementedError(f"Provided unit `{unit}` is not implemented")


total_yt_images = 0
total_hd_images = 0
for dirname, _, filenames in os.walk(YT_IMAGES_DIR):
    for filename in filenames:
        file_path = f"{dirname}/{filename}"
        if os.path.exists(file_path):
            total_yt_images += 1

for dirname, _, filenames in os.walk(IMAGES_DIR):
    for filename in filenames:
        file_path = f"{dirname}/{filename}"
        if os.path.exists(file_path):
            total_hd_images += 1

total_images = total_yt_images + total_hd_images
total_detals = len(glob.glob(f"{DATALAKE_DIR}/details/*.pkl"))

print("==========================================")
print(f"[INFO] total details collected => {total_detals}")
print(f"[INFO] total hd images collected => {total_hd_images}")
print(f"[INFO] total youtube images collected => {total_yt_images}")
print(f"[INFO] total images collected => {total_images}")
print("==========================================")
print("=> Data directory is ", bytes_to_unit(
    get_size(f"{DATALAKE_DIR}"), "KB"))
print("=> Image directory is ", bytes_to_unit(
    get_size(f"{DATALAKE_DIR}/images"), "MB"))
print("=> Video directory is ", bytes_to_unit(
    get_size(f"{DATALAKE_DIR}/yt_videos"), "GB"))
print("==========================================")
# print("Committing to github all the new changes >>>")
# print("==========================================")
# os.system("git add .")
# os.system(f'git commit -m "Update on {total_detals} cows"')
# os.system("git push origin main")
# print("==========================================")
