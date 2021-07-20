import inspect
import os

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# ROOT DIRECTORIES
SRC_DIRNAME = 'src'
ROOT_DIR: str = str(currentdir.split('src')[0])
SRC_DIR = os.path.join(ROOT_DIR, SRC_DIRNAME)

# MODELS
MODEL_DIR = os.path.join(ROOT_DIR, 'models')
MODEL_EXCEL_FILE = os.path.join(MODEL_DIR, 'models.xlsx')

# IMAGES
IMAGE_DIR = os.path.join(ROOT_DIR, 'images')


def make_dir(dir_path):
    """         UTILITY FUNCTION: create a directory if not existing        """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)