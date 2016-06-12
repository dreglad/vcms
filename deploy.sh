# rsync to stging server (La Jornada)

rsync --dry-run -avz --exclude "*.pyc" --exclude "vcms/storage" --exclude "*.mp4" --exclude "src/bin" . root@64.31.10.168:/vagrant

echo 'Any key to proceed, or ctrl+c to cancel...'
read confirmation

rsync -avz --exclude "*.pyc" --exclude "vcms/storage" --exclude "*.mp4" --exclude "src/bin" . root@64.31.10.168:/vagrant

ssh root@64.31.10.168 /etc/init.d/uwsgi reload
ssh root@64.31.10.168 /etc/init.d/memcached restart
ssh root@64.31.10.168 python /vagrant/vcms/manage_lajornadavideos.py collectstatic --noinput
ssh root@64.31.10.168 python /vagrant/vcms/manage_vcms.py collectstatic --noinput

