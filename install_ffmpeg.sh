#!/usr/bin/env bash

# Skip if ffmpeg already installed
if [ -f /usr/local/bin/ffmpeg ]; then
    echo "ffmpeg already installed"
    exit 0
fi

# Install Ffmpeg and required libraries
# From: https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu

# Update APT
sudo apt-get update

# Install dependencies
sudo apt-get -y --force-yes install autoconf automake \
    build-essential libass-dev libfreetype6-dev libtheora-dev \
    libtool libvorbis-dev pkg-config texinfo zlib1g-dev

# Make sources directory
mkdir ~/ffmpeg_sources

# Install Yasm
sudo apt-get install -y yasm

# Install libx264
sudo apt-get install -y libx264-dev

# Install H265/HEVC
sudo apt-get install -y cmake mercurial
cd ~/ffmpeg_sources
hg clone https://bitbucket.org/multicoreware/x265
cd ~/ffmpeg_sources/x265/build/linux
PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_SHARED:bool=off ../../source
make
make install
make distclean

# Install libfdk-aac
cd ~/ffmpeg_sources
wget -O fdk-aac.tar.gz https://github.com/mstorsjo/fdk-aac/tarball/master
tar xzvf fdk-aac.tar.gz
cd mstorsjo-fdk-aac*
autoreconf -fiv
./configure --prefix="$HOME/ffmpeg_build" --disable-shared
make
make install
make distclean

# Install libmp3lame
sudo apt-get install -y libmp3lame-dev

# Install libopus
sudo apt-get install -y libopus-dev

# Install VP8/VP9
cd ~/ffmpeg_sources
wget http://storage.googleapis.com/downloads.webmproject.org/releases/webm/libvpx-1.4.0.tar.bz2
tar xjvf libvpx-1.4.0.tar.bz2
cd libvpx-1.4.0
PATH="$HOME/bin:$PATH" ./configure --prefix="$HOME/ffmpeg_build" --disable-examples --disable-unit-tests
PATH="$HOME/bin:$PATH" make
make install
make clean

# Compile and install ffmpeg
cd ~/ffmpeg_sources
wget http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg
PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
  --prefix="$HOME/ffmpeg_build" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I$HOME/ffmpeg_build/include" \
  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
  --bindir="$HOME/bin" \
  --enable-gpl \
  --enable-libass \
  --enable-libfdk-aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libtheora \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-nonfree
PATH="$HOME/bin:$PATH" make
make install
make distclean
hash -r

# copy binaries
cp $HOME/bin/ffmpeg /usr/local/bin/ffmpeg
cp $HOME/bin/ffprobe /usr/local/bin/ffprobe
