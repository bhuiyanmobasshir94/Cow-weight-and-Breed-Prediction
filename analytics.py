import os
import glob

total_yt_images = 0
total_hd_images = 0
for dirname, _, filenames in os.walk("yt_images"):
    for filename in filenames:
        file_path = f"{dirname}\{filename}"
        if os.path.exists(file_path):
            total_yt_images += 1

for dirname, _, filenames in os.walk("images"):
    for filename in filenames:
        file_path = f"{dirname}\{filename}"
        if os.path.exists(file_path):
            total_hd_images += 1

total_images = total_yt_images + total_hd_images
total_detals = len(glob.glob("details/*.pkl"))

print("==========================================")
print(f"[INFO] total details collected => {total_detals}")
print(f"[INFO] total hd images collected => {total_hd_images}")
print(f"[INFO] total youtube images collected => {total_yt_images}")
print(f"[INFO] total images collected => {total_images}")
print("==========================================")
