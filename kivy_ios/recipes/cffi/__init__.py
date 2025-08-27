# pure-python package, this can be removed when we'll support any python package
from kivy_ios.toolchain import PythonRecipe, shprint
import shutil
import sh
import os

from os import chdir
import logging

logger = logging.getLogger(__name__)


class CFFIRecipe(PythonRecipe):
    version = "1.15.1"
    url = "https://files.pythonhosted.org/packages/2b/a8/050ab4f0c3d4c1b8aaa805f70e26e84d0e27004907c5b8ecc1d31815f92a/cffi-{version}.tar.gz"
    depends = ["python3", "libffi"]
    libraries = [
        "lib_cffi_backend.a"
    ]

    def prebuild_platform(self, plat):
        # common to all archs
        if self.has_marker("patched"):
            return

        self.copy_file("CMakeLists.txt", "c")
        self.copy_file("ios.toolchain.cmake", ".")
        self.set_marker("patched")

    def build_platform(self, plat):
        build_dir = self.get_build_dir(plat)
        logger.info("Building cffi {} in {}".format(plat.arch, build_dir))
        chdir(build_dir)

        os.environ["PATH"] = "/opt/local/bin:/opt/local/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin:/Library/Apple/usr/bin"

        cmake = sh.Command("/usr/local/bin/cmake")
        if plat.arch in ["x86_64"]:
            shprint(cmake, "-Hc", "-G", "Xcode", "-Bbuild",
                    "-DCMAKE_TOOLCHAIN_FILE=" + os.path.join(build_dir, "ios.toolchain.cmake"),
                    "-DPLATFORM=SIMULATOR64")
        else:
            shprint(cmake, "-Hc", "-G", "Xcode", "-Bbuild",
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
    
    # def create_xcframeworks(self):
    #     logger.info("Skipping xcframework creation for cffi due to duplicate architecture identifiers")
    #     # Skip xcframework creation for cffi as both iphoneos-arm64 and iphonesimulator-arm64
    #     # would result in the same ios-arm64 identifier, causing xcodebuild conflicts
    #     pass

recipe = CFFIRecipe()
