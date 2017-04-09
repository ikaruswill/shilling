cd ~/www/
uwsgi -s /tmp/shilling.ikaruswill.com.sock --manage-script-name --mount /=app:app  -H /home/shilling/env/ --chmod-socket=666 --daemonize /tmp/shilling.log --pidfile /tmp/shilling.pid --touch-reload /home/shilling/uwsgi-reload
