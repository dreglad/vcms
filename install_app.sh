#!/usr/bin/env bash

# Create storage directories
mkdir /storage && chmod 777 /storage
mkdir /storage/static && chmod 777 /storage/static
mkdir /storage/clips && chmod 777 /storage/clips
mkdir /storage/images && chmod 777 /storage/images
mkdir /storage/temp && chmod 777 /storage/temp
mkdir /storage/temp/status && chmod 777 /storage/temp/status
mkdir /storage/sprites && chmod 777 /storage/sprites
mkdir /storage/hls && chmod 777 /storage/hls

# Create database
echo "CREATE DATABASE video" | mysql -u root -ppass

# Prepare env
cd /vagrant/src
virtualenv --no-site-packages --python /usr/bin/python-2.7 .
source ./bin/activate

# Install python dependencies
pip install -r requirements.txt

# Data and migrations
./manage.py makemigrations
./manage.py migrate
./manage.py loaddata users tipo_clips tipo_programas categorias paises programas corresponsales servicios

./manage.py collectstatic --noinput

# Configure web server
cp /vagrant/etc/apache.video.conf /etc/apache2/sites-available/video.conf
a2ensite video
service apache2 reload
