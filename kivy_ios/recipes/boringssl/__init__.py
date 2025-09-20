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
pyBoringSSL_path = os.path.abspath(os.path.join(root_path, os.path.pardir, os.path.pardir, "pyBoringSSL"))


class BoringSSLRecipe(CythonRecipe):
    version = "1.1.1"
    url = "https://github.com/XX-Net/pyBoringSSL/archive/{version}.zip"
    depends = ["python"]
    libraries = [
        "libbssl.a",
        "libbcrypto.a",
        "libdecrepit.a",

        "libbrotlicommon.a",
        "libbrotlidec.a",

        "libcert_decompress.a",
        "libgetpeercert.a",
        "libcffi_boringssl.a",
    ]
    custom_dir = pyBoringSSL_path
    boringssl_version = "1.1.0"
    brotli_version = "1.0.9"

    # def download(self):
    #     # TODO: download if local ../pyBoringSSL not exist.
    #     pass

    def extract_platform(self, plat):
        def ignore(src, names):
            # print(src, names)
            if src.endswith("pyBoringSSL") and "build" in names:
                return ["build", ".git", ]
            else:
                return set()

        build_dir = join(self.ctx.build_dir, self.name, plat.name)
        dest_dir = join(build_dir, self.archive_root)
        if self.custom_dir:
            shutil.rmtree(dest_dir, ignore_errors=True)
            shutil.copytree(self.custom_dir, dest_dir, ignore=ignore)
        else:
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir, ignore_errors=True)

            src_dir = join(self.recipe_dir, self.url)
            if os.path.exists(src_dir):
                shutil.copytree(src_dir, dest_dir)
                return
            ensure_dir(build_dir)
            self.extract_file(self.archive_fn, build_dir)

    def prebuild_platform(self, plat):
        build_dir = self.get_build_dir(plat)
        if not os.path.isfile(os.path.join(build_dir, "boringssl", "CMakeLists.txt")):
            self.download_file(f"https://github.com/XX-net/boringssl/archive/refs/tags/{self.boringssl_version}.zip", "boringssl.zip", build_dir)
            self.extract_file("boringssl.zip", build_dir)
            shutil.rmtree(os.path.join(build_dir, "boringssl"))
            os.rename(os.path.join(build_dir, f"boringssl-{self.boringssl_version}"), os.path.join(build_dir, "boringssl"))

        if not os.path.isfile(os.path.join(build_dir, "brotli", "CMakeLists.txt")):
            self.download_file(f"https://github.com/google/brotli/archive/refs/tags/v{self.brotli_version}.zip", "brotli.zip", build_dir)
            self.extract_file("brotli.zip", build_dir)
            shutil.rmtree(os.path.join(build_dir, "brotli"))
            os.rename(os.path.join(build_dir, f"brotli-{self.brotli_version}"), os.path.join(build_dir, "brotli"))

    def build_platform(self, plat):
        build_dir = self.get_build_dir(plat)
        logger.info("Building BoringSSL {} in {}".format(plat.arch, build_dir))
        chdir(build_dir)
        symbols_fp = os.path.join(build_dir, "boringssl_symbols.txt")

        os.environ["PATH"] = "/opt/local/bin:/opt/local/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin:/Library/Apple/usr/bin"

        cmake = sh.Command("/usr/local/bin/cmake")
        if plat.arch in ["x86_64"]:
            shprint(cmake, "-G", "Xcode", "-Bbuild", "-DCMAKE_TOOLCHAIN_FILE=ios.toolchain.cmake",
                    "-DPLATFORM=SIMULATOR64",
                    '-DBORINGSSL_PREFIX=BSSL',
                    "-DBORINGSSL_PREFIX_SYMBOLS=" + symbols_fp,
                    )
        else:
            shprint(cmake, "-G", "Xcode", "-Bbuild", "-DCMAKE_TOOLCHAIN_FILE=ios.toolchain.cmake",
                    "-DPLATFORM=OS64",
                    '-DBORINGSSL_PREFIX=BSSL',
                    "-DBORINGSSL_PREFIX_SYMBOLS=" + symbols_fp,
                    )

        build_ios_lib = sh.Command(os.path.join(build_dir, "build_ios_lib.zsh"))
        shprint(build_ios_lib)
        print("build " + plat.arch)

    def postbuild_platform(self, plat):
        build_dir = self.get_build_dir(plat)

        libraries = [
            "build/boringssl/ssl/Release-iphoneos/libssl.a",
            "build/boringssl/crypto/Release-iphoneos/libcrypto.a",
            "build/boringssl/decrepit/Release-iphoneos/libdecrepit.a",

            "build/brotli/Release-iphoneos/libbrotlicommon.a",
            "build/brotli/Release-iphoneos/libbrotlidec.a",

            "build/cert_decompress/Release-iphoneos/libcert_decompress.a",
            "build/getpeercert/Release-iphoneos/libgetpeercert.a",
            "build/cffi_boringssl/Release-iphoneos/libcffi_boringssl.a",
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
            if fn == "libssl.a":
                fn = "libbssl.a"
            elif fn == "libcrypto.a":
                fn = "libbcrypto.a"
            dst = os.path.join(build_dir, fn)
            shutil.copyfile(src, dst)

    def install(self):
        pass


recipe = BoringSSLRecipe()
