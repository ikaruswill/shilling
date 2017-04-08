uwsgi -s /tmp/shilling.ikaruswill.com.sock --manage-script-name --mount /=app:app  --virtualenv /home/shilling/venv/ --chmod-socket=666
