
#rsync -n --delete -avz --exclude "vcms/storage" --exclude "*.pyc" --exclude "*.mp4" --exclude "src/bin" . root@64.31.10.168:/vagrant

#read confirmation

rsync -avz --exclude "*.pyc" --exclude "vcms/storage" --exclude "*.mp4" --exclude "src/bin" . root@64.31.10.168:/vagrant

ssh root@64.31.10.168 /etc/init.d/uwsgi restart # reload
ssh root@64.31.10.168 /etc/init.d/memcached restart
ssh root@64.31.10.168 python /vagrant/vcms/manage_lajornadavideos.py collectstatic --noinput
ssh root@64.31.10.168 python /vagrant/vcms/manage_vcms.py collectstatic --noinput

