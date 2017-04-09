#!/bin/bash
while [ ! -f ./.pem_path ]; do
	read -p "Enter path to pem: " pem_path
	if [ -f $pem_path ]; then
		echo $pem_path > ./.pem_path
	else
		echo "pem file not found or is in private directory"
	fi
done

pem_path=$(cat ./.pem_path)

case $1 in
	start)
		echo "Starting server..."
		ssh -i $pem_path shilling@ikaruswill.com 'bash' < ./uwsgi_control/start.sh
		;;
	stop)
		echo "Stopping server..."
		ssh -i $pem_path shilling@ikaruswill.com 'bash' < ./uwsgi_control/stop.sh
		;;
	restart)
		echo "Restarting server..."
		ssh -i $pem_path shilling@ikaruswill.com 'bash' < ./uwsgi_control/restart.sh
		;;
	ssh)
		echo "Connecting to server..."
		ssh -i $pem_path shilling@ikaruswill.com
		;;
	sync)
		echo "Syncing to server..."
		rsync -e "ssh -i $pem_path" -rithp --stats --exclude '*.git' --exclude '.*' --exclude '__*' ./ shilling@ikaruswill.com:~/www/
		echo "Restarting server..."
		ssh -i $pem_path shilling@ikaruswill.com 'bash' < ./uwsgi_control/restart.sh # RESTART
		echo "Updating tokens..."
		ssh -i $pem_path shilling@ikaruswill.com 'cd ~/www; ./update_token.sh' # UPDATE TOKENS
		;;
	tokens)
		echo "Updating tokens..."
		ssh -i $pem_path shilling@ikaruswill.com 'cd ~/www; ./update_token.sh'
		;;
esac