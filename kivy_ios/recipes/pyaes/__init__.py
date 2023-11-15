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
    version = "1.0.1"

    url = "https://github.com/XX-net/pyAES/archive/{version}.zip"
    depends = ["python"]
    libraries = [
        "libpyaes.a",
        "libcryptopp.a",
        "libaes_cfb.a",
    ]
    cryptopp_version = "8.9"

    def download(self):
        pass

    def extract(self):
        pass

    def extract_arch(self, arch):
        # Copy pyAES from parent dir.

        def ignore(src, names):
            # print(src, names)
            if src.endswith("pyAES") and "build" in names:
                return ["build", ".git", ]
            else:
                return set()

        logger.debug("pyAES path:%s", pyAES_path)
        if os.path.isdir(pyAES_path):
            build_dir = join(self.ctx.build_dir, self.name, arch)
            dest_dir = join(build_dir, self.archive_root)
            shutil.rmtree(dest_dir, ignore_errors=True)
            shutil.copytree(pyAES_path, dest_dir, ignore=ignore)

    def prebuild_arch(self, arch):
        logger.debug("pyaes prebuild %s", arch)
        # download cryptopp if not downloaded.
        build_dir = self.get_build_dir(arch.arch)
        if not os.path.isfile(os.path.join(build_dir, "cryptopp", "aes.h")):
            self.download_file(f"https://github.com/XX-net/cryptopp/archive/refs/tags/{self.cryptopp_version}.zip", "cryptopp.zip", build_dir)
            self.extract_file("cryptopp.zip", build_dir)
            shutil.rmtree(os.path.join(build_dir, "cryptopp"))
            os.rename(os.path.join(build_dir, f"cryptopp-{self.cryptopp_version}"), os.path.join(build_dir, "cryptopp"))

    def build_cryptopp(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        chdir(build_dir)

        os.environ["IOS_SDK"] = "iPhoneOS"

        if arch.arch in ["x86_64"]:
            os.environ["IOS_CPU"] = "x86_64"
        else:
            os.environ["IOS_CPU"] = "arm64"
        # IOS_SDK=iPhoneOS IOS_CPU=arm64 source TestScripts/setenv-ios.sh
        # make

        build_ios_lib = sh.Command(os.path.join(build_dir, "build_cryptopp_ios.sh"))
        shprint(build_ios_lib)

    def build_aes_cfb(self, arch):
        # cmake -G Xcode -Bbuild -DCMAKE_TOOLCHAIN_FILE=ios.toolchain.cmake  -DPLATFORM=OS64 -DCMAKE_SYSTEM_NAME=iOS -DCMAKE_Swift_COMPILER_FORCED=true -DCMAKE_OSX_DEPLOYMENT_TARGET=12.0
        cmake = sh.Command("/usr/local/bin/cmake")
        if arch.arch in ["x86_64"]:
            shprint(cmake, "-G", "Xcode", "-Bbuild_aes", "-DCMAKE_TOOLCHAIN_FILE=ios.toolchain.cmake",
                    "-DPLATFORM=SIMULATOR64",
                    )
        else:
            shprint(cmake, "-G", "Xcode", "-Bbuild_aes", "-DCMAKE_TOOLCHAIN_FILE=ios.toolchain.cmake",
                    "-DPLATFORM=OS64",
                    )

        # cmake --build build -v -j8 --config Release --target aes_cfb
        shprint(cmake, "--build", "build_aes", "--config", "Release", "--target", "aes_cfb")

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        logger.info("Building pyAES {} in {}".format(arch.arch, build_dir))
        chdir(build_dir)

        os.environ["PATH"] = "/opt/local/bin:/opt/local/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin:/Library/Apple/usr/bin"

        super().build_arch(arch)

        self.build_cryptopp(arch)

        self.build_aes_cfb(arch)

    def postbuild_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)

        shutil.copyfile(
            join(build_dir, "cryptopp", "libcryptopp.a"),
            join(build_dir, "libcryptopp.a")
            )

        if arch.arch in ["x86_64"]:
            shutil.copyfile(
                join(build_dir, "build_aes", "aes_cfb", "Release-iphonesimulator", "libaes_cfb.a"),
                join(build_dir, "libaes_cfb.a")
            )
        else:
            shutil.copyfile(
                join(build_dir, "build_aes", "aes_cfb", "Release-iphoneos", "libaes_cfb.a"),
                join(build_dir, "libaes_cfb.a")
            )
        super().postbuild_arch(arch)

    def install(self):
        # put an empty so file
        dst = os.path.join(self.ctx.site_packages_dir, "py_aes_cfb.so")
        with open(dst, "w") as fd:
            fd.write(" ")


recipe = pyAESRecipe()
