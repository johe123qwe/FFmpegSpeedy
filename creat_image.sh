#!/bin/bash

# 安装 brew install create-dmg
# rm -rf build dist  && pyinstaller build.spec && bash creat_image.sh
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# brew install create-dmg
mkdir -p ./dist/dmg

rm -r ./dist/dmg/*
cp -r "dist/FFmpegSpeedy.app" dist/dmg 
test -f "dist/FFmpegSpeedy.dmg" && rm "dist/FFmpegSpeedy.dmg"
create-dmg \
  --volname "FFmpegSpeedy" \
  --volicon "./src/logo.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "FFmpegSpeedy.app" 175 120 \
  --hide-extension "FFmpegSpeedy.app" \
  --app-drop-link 425 120 \
  "dist/FFmpegSpeedy.dmg" \
  "dist/dmg/"