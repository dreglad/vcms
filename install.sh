#!/usr/bin/env bash

# Add PPA repository for ffmpeg and codecs
add-apt-repository -y ppa:mc3man/trusty-media

# Update APT cache and upgrade packages
apt-get update
apt-get -y dist-upgrade

# Install packages
debconf-set-selections <<< 'mysql-server mysql-server/root_password password pass'
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password pass'
apt-get install -y python-virtualenv redis-server libjpeg-dev python-dev \
    libyaml-dev imagemagick mysql-server libmysqlclient-dev \
    ffmpeg x264 fdkaac-encoder apache2-mpm-prefork libapache2-mod-wsgi

# Create storage directories
mkdir /storage /storage/static /storage/clips /storage/images /storage/temp \
    /storage/temp/status /storage/sprites /storage/hls /var/log/video
chmod -R 777 /storage /var/log/video

# Create database
echo "CREATE DATABASE video" | mysql -u root -ppass

# Prepare env
cd /vagrant/src
rm -rf bin include local lib
virtualenv --no-site-packages --python /usr/bin/python2.7 .
source ./bin/activate

# Install python dependencies
pip install -r requirements.txt

# Migrate and load data
./manage.py migrate
./manage.py loaddata users tipo_clips tipo_programas categorias paises programas corresponsales servicios
./manage.py collectstatic --noinput

# django supervisor upstart
cp /vagrant/etc/etc--init--django-supervisor.conf /etc/init/django-supervisor.conf
cp /vagrant/etc/etc--init--workaround-vagrant-bug-6074.conf /etc/init/workaround-vagrant-bug-6074.conf
initctl reload-configuration
start workaround-vagrant-bug-6074
start django-supervisor

# Configure web server
cp /vagrant/etc/apache.video.conf /etc/apache2/sites-available/video.conf
a2ensite video
service apache2 reload
