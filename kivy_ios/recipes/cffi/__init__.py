# pure-python package, this can be removed when we'll support any python package
from kivy_ios.toolchain import PythonRecipe, shprint
import shutil
import sh
import os

from os import chdir
import logging

logger = logging.getLogger(__name__)


class CFFIRecipe(PythonRecipe):
    version = "1.17.1"
    url = "https://files.pythonhosted.org/packages/fc/97/c783634659c2920c3fc70419e3af40972dbaf758daa229a7d6ea6135c90d/cffi-1.17.1.tar.gz"
    depends = ["python3", "libffi"]
    libraries = [
        "lib_cffi_backend.a"
    ]

    def prebuild_platform(self, plat):
        # common to all archs
        if self.has_marker("patched"):
            return

        self.copy_file("CMakeLists.txt", "src/c/.")
        self.copy_file("ios.toolchain.cmake", ".")
        self.set_marker("patched")

    def build_platform(self, plat):
        build_dir = self.get_build_dir(plat)
        logger.info("Building cffi {} in {}".format(plat.arch, build_dir))
        chdir(build_dir)

        os.environ[
            "PATH"] = "/opt/local/bin:/opt/local/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin:/Library/Apple/usr/bin"

        cmake = sh.Command("/usr/local/bin/cmake")
        if plat.arch in ["x86_64"]:
            shprint(cmake, "-Hsrc/cc", "-G", "Xcode", "-Bbuild",
                    "-DCMAKE_TOOLCHAIN_FILE=" + os.path.join(build_dir, "ios.toolchain.cmake"),
                    "-DPLATFORM=SIMULATOR64")
        else:
            shprint(cmake, "-Hsrc/c", "-G", "Xcode", "-Bbuild",
                    "-DCMAKE_TOOLCHAIN_FILE=" + os.path.join(build_dir, "ios.toolchain.cmake"),
                    "-DPLATFORM=OS64")

        shprint(cmake, "--build", "build", "--config", "Release")
        print("build " + plat.arch)

    def postbuild_platform(self, plat):
        build_dir = self.get_build_dir(plat)

        libraries = [
            "build/Release-iphoneos/lib_cffi_backend.a",
        ]

        for fp in libraries:
            fpl = fp.split("/")
            if plat.arch == "x86_64":
                fpl[-2] = "Release-iphonesimulator"
            else:
                fpl[-2] = "Release-iphoneos"

            fp = "/".join(fpl)
            src = os.path.join(build_dir, fp)

            fn = fpl[-1]
            dst = os.path.join(build_dir, fn)
            shutil.copyfile(src, dst)

    def install(self):
        logger.info("Install mock modules: _cffi_backend")
        dst = os.path.join(self.ctx.site_packages_dir, "_cffi_backend.so")
        with open(dst, "w") as fd:
            fd.write(" ")


recipe = CFFIRecipe()
