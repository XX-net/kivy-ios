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
pyAES_path = os.path.abspath(os.path.join(root_path, os.path.pardir, os.path.pardir, "pyaes"))


class pyAESRecipe(CythonRecipe):
    version = "1.0.2"

    url = "https://github.com/XX-net/pyAES/archive/{version}.zip"
    depends = ["python"]
    libraries = [
        "libpyaes.a",
        "libcryptopp.a",
        "libaes_cfb.a",
    ]
    cryptopp_version = "8.9"

    @property
    def archive_root(self):
        return f"pyAES-{self.version}"

    def download(self):
        pass

    def extract(self):
        # Call the parent extract which will call extract_platform for each platform
        super().extract()

    def extract_platform(self, plat):
        # Copy pyAES from parent dir.

        def ignore(src, names):
            # print(src, names)
            if src.endswith("pyAES") and "build" in names:
                return ["build", ".git", ]
            else:
                return set()

        logger.debug("pyAES path:%s", pyAES_path)
        if os.path.isdir(pyAES_path):
            build_dir = join(self.ctx.build_dir, self.name, plat.name)
            dest_dir = join(build_dir, self.archive_root)
            shutil.rmtree(dest_dir, ignore_errors=True)
            shutil.copytree(pyAES_path, dest_dir, ignore=ignore)

    def prebuild_platform(self, plat):
        logger.debug("pyaes prebuild %s", plat.name)
        # download cryptopp if not downloaded.
        build_dir = self.get_build_dir(plat)
        if not os.path.isfile(os.path.join(build_dir, "cryptopp", "aes.h")):
            self.download_file(f"https://github.com/XX-net/cryptopp/archive/refs/tags/{self.cryptopp_version}.zip", "cryptopp.zip", build_dir)
            self.extract_file("cryptopp.zip", build_dir)
            shutil.rmtree(os.path.join(build_dir, "cryptopp"))
            os.rename(os.path.join(build_dir, f"cryptopp-{self.cryptopp_version}"), os.path.join(build_dir, "cryptopp"))

    def build_cryptopp(self, plat):
        build_dir = self.get_build_dir(plat)
        cryptopp_dir = os.path.join(build_dir, "cryptopp")
        chdir(cryptopp_dir)

        make_env = plat.get_env()
        make_env["IOS_SDK"] = "iPhoneOS"
        make_env["IOS_CPU"] = "arm64"
        shprint(sh.make, "static", self.ctx.concurrent_make, _env=make_env)

    def build_aes_cfb(self, plat):
        build_dir = self.get_build_dir(plat)
        chdir(build_dir)
        
        toolchain_file = os.path.join(build_dir, "ios.toolchain.cmake")
        
        cmake = sh.Command("/usr/local/bin/cmake")
        if plat.arch in ["x86_64"]:
            shprint(cmake, "-G", "Xcode", "-Bbuild_aes", f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}",
                    "-DPLATFORM=SIMULATOR64", "aes_cfb")
        else:
            shprint(cmake, "-G", "Xcode", "-Bbuild_aes", f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}",
                    "-DPLATFORM=OS64", "aes_cfb")

        # cmake --build build -v -j8 --config Release --target aes_cfb
        shprint(cmake, "--build", "build_aes", "--config", "Release", "--target", "aes_cfb")

    def build_platform(self, plat):
        build_dir = self.get_build_dir(plat)
        logger.info("Building pyAES {} in {}".format(plat.arch, build_dir))
        chdir(build_dir)

        os.environ["PATH"] = "/opt/local/bin:/opt/local/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin:/Library/Apple/usr/bin"

        super().build_platform(plat)

        self.build_cryptopp(plat)

        self.build_aes_cfb(plat)

    def postbuild_platform(self, plat):
        build_dir = self.get_build_dir(plat)

        shutil.copyfile(
            join(build_dir, "cryptopp", "libcryptopp.a"),
            join(build_dir, "libcryptopp.a")
            )

        if plat.arch in ["x86_64"]:
            shutil.copyfile(
                join(build_dir, "build_aes", "Release-iphonesimulator", "libaes_cfb.a"),
                join(build_dir, "libaes_cfb.a")
            )
        else:
            shutil.copyfile(
                join(build_dir, "build_aes", "Release-iphoneos", "libaes_cfb.a"),
                join(build_dir, "libaes_cfb.a")
            )
        super().postbuild_platform(plat)

    def install(self):
        # put an empty so file
        dst = os.path.join(self.ctx.site_packages_dir, "py_aes_cfb.so")
        with open(dst, "w") as fd:
            fd.write(" ")


recipe = pyAESRecipe()
