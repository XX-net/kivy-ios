import shutil

from kivy_ios.toolchain import CythonRecipe, shprint, ensure_dir
from os.path import join
import sh
import os
from os import chdir
import logging

logger = logging.getLogger(__name__)

current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_path, os.path.pardir, os.path.pardir, os.path.pardir))


class MbedtlsRecipe(CythonRecipe):
    version = "2.5.0"
    url = "https://github.com/Synss/python-mbedtls/archive/refs/tags/{version}.zip"
    depends = ["python"]
    libraries = [
    ]

    # custom_dir = pyBoringSSL_path
    # boringssl_version = "1.1.0"
    # brotli_version = "1.0.9"


recipe = MbedtlsRecipe()
