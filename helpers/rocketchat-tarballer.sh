#!/usr/bin/env bash
version=4.9.1

tar -xzf $version.tar.gz
cd Rocket.Chat.Electron-$version/
yarn install --immutable --mode=skip-build
tar -czf rocketchat-desktop-$version-yarn-cache.tar.xz .yarn/
mv rocketchat-desktop-$version-yarn-cache.tar.xz ../rocketchat-desktop-$version-yarn-cache.tar.xz
