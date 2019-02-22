@echo on

call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars64.bat"
set MINICONDA="C:\Miniconda3-x64"
set PATH=%MINICONDA%;%MINICONDA%/Scripts/;%MINICONDA%/Library/bin;%PATH%
set LIB=%MINICONDA%/Library/lib;%LIB%
set CPATH=%MINICONDA%/Library/include;%CPATH%
set CC=clang-cl
set CXX=clang-cl
set CFLAGS=-m64 -fmsc-version=1916
set CXXFLAGS=-m64 -fmsc-version=1916
set CONAN_CMAKE_GENERATOR=Ninja
conan create . kudzurunner/stable -s compiler=clang -s compiler.libcxx=libstdc++ -s compiler.version=5.0 -s build_type=Debug
conan create . kudzurunner/stable -s compiler=clang -s compiler.libcxx=libstdc++ -s compiler.version=5.0 -s build_type=Release