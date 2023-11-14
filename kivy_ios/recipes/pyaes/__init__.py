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
        # "libcryptopp.a",
    ]
    cryptopp_version = "8.9"

    def extract_arch(self, arch):
        def ignore(src, names):
            # print(src, names)
            if src.endswith("pyAES") and "build" in names:
                return ["build", ".git", ]
            else:
                return set()

        build_dir = join(self.ctx.build_dir, self.name, arch)
        dest_dir = join(build_dir, self.archive_root)
        shutil.rmtree(dest_dir, ignore_errors=True)
        shutil.copytree(pyAES_path, dest_dir, ignore=ignore)

    def prebuild_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        if not os.path.isfile(os.path.join(build_dir, "cryptopp", "aes.h")):
            self.download_file(f"https://github.com/XX-net/cryptopp/archive/refs/tags/{self.cryptopp_version}.zip", "cryptopp.zip", build_dir)
            self.extract_file("cryptopp.zip", build_dir)
            shutil.rmtree(os.path.join(build_dir, "cryptopp"))
            os.rename(os.path.join(build_dir, f"cryptopp-{self.cryptopp_version}"), os.path.join(build_dir, "cryptopp"))

    def build_arch(self, arch):
        # zsh = sh.Command("/bin/zsh")
        # shprint(zsh)
        # os.system("zsh")

        super().build_arch(arch)
        # build_dir = self.get_build_dir(arch.arch)
        # logger.info("Building pyAES {} in {}".format(arch.arch, build_dir))
        # chdir(build_dir)
        # 
        # os.environ["PATH"] = "/opt/local/bin:/opt/local/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin:/Library/Apple/usr/bin"
        # 
        # cmake = sh.Command("/usr/local/bin/make")
        # if arch.arch in ["x86_64"]:
        #     shprint(cmake, "-G", "Xcode", "-Bbuild", "-DCMAKE_TOOLCHAIN_FILE=ios.toolchain.cmake",
        #             "-DPLATFORM=SIMULATOR64",
        #             '-DBORINGSSL_PREFIX=BSSL',
        #             "-DBORINGSSL_PREFIX_SYMBOLS=" + symbols_fp,
        #             )
        # else:
        #     shprint(cmake, "-G", "Xcode", "-Bbuild", "-DCMAKE_TOOLCHAIN_FILE=ios.toolchain.cmake",
        #             "-DPLATFORM=OS64",
        #             '-DBORINGSSL_PREFIX=BSSL',
        #             "-DBORINGSSL_PREFIX_SYMBOLS=" + symbols_fp,
        #             )
        # 
        # build_ios_lib = sh.Command(os.path.join(build_dir, "build_ios_lib.zsh"))
        # shprint(build_ios_lib)
        # print("build " + arch.arch)

    def postbuild_arch(self, arch):
        super().postbuild_arch(arch)
    #     build_dir = self.get_build_dir(arch.arch)
    #
    #     libraries = [
    #         "build/boringssl/ssl/Release-iphoneos/libssl.a",
    #         "build/boringssl/crypto/Release-iphoneos/libcrypto.a",
    #         "build/boringssl/decrepit/Release-iphoneos/libdecrepit.a",
    #
    #         "build/brotli/Release-iphoneos/libbrotlicommon.a",
    #         "build/brotli/Release-iphoneos/libbrotlidec.a",
    #
    #         "build/cert_decompress/Release-iphoneos/libcert_decompress.a",
    #         "build/getpeercert/Release-iphoneos/libgetpeercert.a",
    #         "build/cffi_boringssl/Release-iphoneos/libcffi_boringssl.a",
    #     ]
    #
    #     for fp in libraries:
    #         fpl = fp.split("/")
    #         if arch.arch == "x86_64":
    #             fpl[-2] = "Release-iphonesimulator"
    #         else:
    #             fpl[-2] = "Release-iphoneos"
    #
    #         fp = "/".join(fpl)
    #         src = os.path.join(build_dir, fp)
    #
    #         fn = fpl[-1]
    #         if fn == "libssl.a":
    #             fn = "libbssl.a"
    #         elif fn == "libcrypto.a":
    #             fn = "libbcrypto.a"
    #         dst = os.path.join(build_dir, fn)
    #         shutil.copyfile(src, dst)

    # def install(self):
    #     dst = os.path.join(self.ctx.site_packages_dir, "boringssl.so")
    #     with open(dst, "w") as fd:
    #         fd.write(" ")


recipe = pyAESRecipe()
