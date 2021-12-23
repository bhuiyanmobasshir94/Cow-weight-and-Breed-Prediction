import os
import sys

import requests

from configs import *
from extractor import extract


def download(url, file_path):
    try:
        gz_file_path = file_path + ".tar.gz"
        r = requests.get(url, stream=True)
        with open(gz_file_path, "wb") as f:
            for chunk in r.raw.stream(1024, decode_content=False):
                if chunk:
                    f.write(chunk)
        logger.info(
            "Downloaded file from %s to %s", url, gz_file_path
        )
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    extract(DATALAKE_DIR, gz_file_path)
    os.remove(gz_file_path)
