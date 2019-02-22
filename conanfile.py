from conans import ConanFile, CMake, tools
import shutil
import os

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class OpenblasConan(ConanFile):
    name = "openblas"
    version = "0.3.5"
    license = "https://raw.githubusercontent.com/xianyi/OpenBLAS/develop/LICENSE"
    author = "KudzuRunner"
    url = "https://github.com/kudzurunner/conan-openblas"
    description = "OpenBLAS is an optimized BLAS library based on GotoBLAS2 1.13 BSD version"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "visual_studio": [True, False]}
    default_options = {"shared": True, "visual_studio": True}
    generators = "cmake"

    source_name = "OpenBLAS-{}".format(version)
    suffix = ""

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("strawberryperl/5.28.1.1@kudzurunner/stable")

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            raise Exception("Only shared build supported in Visual Studio")
        if self.settings.compiler == "Visual Studio" and not self.options.visual_studio:
            raise Exception("This library needs option 'visual_studio=True' to be consumed")

    def source(self):
        archive_name = "v{}.tar.gz".format(self.version)
        url = "https://github.com/xianyi/OpenBLAS/archive/{}".format(archive_name)

        tools.download(url, filename=archive_name)
        tools.untargz(filename=archive_name)
        os.remove(archive_name)

        self.suffix = ("_d" if self.settings.build_type == "Debug" else "")
        tools.replace_in_file(
            "{}/CMakeLists.txt".format(self.source_name), "project(OpenBLAS C ASM)",
            '''project(OpenBLAS C ASM)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
if(NOT CMAKE_DEBUG_POSTFIX)
  set(CMAKE_DEBUG_POSTFIX %s)
endif()''' % self.suffix)

        tools.replace_in_file(
            "{}/utest/CMakeLists.txt".format(self.source_name), "if (MSVC)",
            "if (MSVC AND NOT \"${CMAKE_C_COMPILER_ID}\" MATCHES Clang)")

    def build(self):
        os.mkdir("build")
        shutil.move("conanbuildinfo.cmake", "build/")
        cmake = CMake(self)
        cmake.definitions["DYNAMIC_ARCH"] = "ON"
        cmake.definitions["USE_THREAD"] = "OFF"
        cmake.definitions["BUILD_WITHOUT_LAPACK"] = "OFF"
        cmake.definitions["NOFORTRAN"] = "OFF"
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        cmake.configure(source_folder=self.source_name, build_folder="build")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_name, keep_path=False, ignore_case=True)

        out = StringIO()
        try:
            self.run("where flang.dll", output=out)
        except Exception as e:
            raise Exception("Failed to get flang.dll path: [{0}]{1}".format(e, out.getvalue()))

        libdir = os.path.dirname(os.path.normpath(out.getvalue().strip()))
        self.copy(pattern="flang.dll", dst="bin", src=libdir, keep_path=False)
        self.copy(pattern="flangrti.dll", dst="bin", src=libdir, keep_path=False)
        self.copy(pattern="libomp.dll", dst="bin", src=libdir, keep_path=False)

    def package_info(self):
        try:
            shutil.move("lib64", "lib")
        except Exception:
            pass

        self.cpp_info.includedirs = ["include/openblas"]
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

    def package_id(self):
        if self.options.visual_studio:
            self.info.settings.compiler = "Visual Studio"
            self.info.settings.compiler.version = "ANY"
            self.info.settings.compiler.runtime = "ANY"
            self.info.settings.compiler.toolset = "ANY"