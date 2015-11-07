#!/usr/bin/env bash

# Install packages
apt-get install -y python-virtualenv redis-server libjpeg-dev python-dev libyaml-dev

# MySQL
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password pass'
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password pass'
sudo apt-get -y install mysql-server libmysqlclient-dev

# Apache
apt-get install -y apache2-mpm-prefork libapache2-mod-wsgi
