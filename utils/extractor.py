import gzip
import shutil
import tarfile
import zipfile

from configs import *

ZIP_EXTENSION = ".zip"
TAR_EXTENSION = ".tar"
TAR_GZ_EXTENSION = ".tar.gz"
TGZ_EXTENSION = ".tgz"
GZ_EXTENSION = ".gz"
UNKNOWN_FORMAT = "Unknown file format. Can't extract."


def extract(folder_path, gz_file_path):
    if gz_file_path.endswith(ZIP_EXTENSION):
        logger.info("Extracting zip file.")
        zipf = zipfile.ZipFile(gz_file_path, "r")
        zipf.extractall(folder_path)
        zipf.close()
    elif (
        gz_file_path.endswith(TAR_EXTENSION)
        or gz_file_path.endswith(TAR_GZ_EXTENSION)
        or gz_file_path.endswith(TGZ_EXTENSION)
    ):
        logger.info("Extracting tar file.")
        tarf = tarfile.open(gz_file_path, "r")
        tarf.extractall(folder_path)
        tarf.close()
    elif gz_file_path.endswith(GZ_EXTENSION):
        logger.info("Extracting gz file.")
        out_file = gz_file_path[:-3]
        with gzip.open(gz_file_path, "rb") as f_in:
            with open(out_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        logger.warning(UNKNOWN_FORMAT)


def make_tar(source_path):
    gz_path = source_path + ".tar.gz"
    with tarfile.open(gz_path, "w:gz") as tar:
        tar.add(source_path)
    return gz_path
