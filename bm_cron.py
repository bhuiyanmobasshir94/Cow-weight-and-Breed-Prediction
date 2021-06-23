import os
import time

from pathlib import Path, WindowsPath

BASE_DIR = Path(__file__).resolve().parent

for offset in range(0,300):
    os.system(f'node cattle_link_scraper.js {offset}')
    file_name = BASE_DIR/"bm_cache"/f'card_{offset}.txt'
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            content = f.read()
            if len(content) > 0:
                print(f"Ok {offset}")
                continue
            else:
                os.system(f'node cattle_link_scraper.js {offset}')
    else:
        os.system(f'node cattle_link_scraper.js {offset}')
    time.sleep(20)