#!/usr/bin/env bash

# src: https://www.peterspython.com/en/blog/using-pyinstaller-and-cython-to-create-a-python-executable

set -v
set -e

# first build with cython. Not required but let's be bold
python cython-setup.py build_ext --inplace

# package with pyinstaller into a directory (no --nofile) which ensure speedy bootstrap
# NOTE packaging with --onefile produces significantly slower binary
pyinstaller \
    --hiddenimport glob --hiddenimport difflib \
    --name="xyc" --add-binary="xyc/*.so:xyc/" --add-data="xyc/libs:xyc/libs" \
    xyc/xyc.py

## and then for the "coup de grace" package again using AppImage in order to have a single executable file
#ln -s xyc dist/xyc/AppRun
#cat <<EOF > dist/xyc/xyc.desktop
#[Desktop Entry]
#Name=xyc
#Exec=xyc
#Icon=icon-xyc
#Type=Application
#Categories=Utility;Application;
#EOF
#wget "https://www.xy-lang.org/images/logo.svg" -O "dist/xyc/icon-xyc.svg"
#
#wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage -O build/linuxdeploy-x86_64.AppImage
#chmod u+x build/linuxdeploy-x86_64.AppImage
#./build/linuxdeploy-x86_64.AppImage --appdir dist/xyc --output appimage

#mkdir -p bin
#mv xyc-x86_64.AppImage bin/xyc-x86_64

cd dist/xyc && tar -cvzf ../../xyc-$(uname | awk '{print tolower($0)}').tar.gz *
