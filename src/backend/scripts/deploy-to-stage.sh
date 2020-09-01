#!/usr/bin/env bash
set -euo pipefail

DIST='../dist'
if [[ -d $DIST ]]; then
    echo "Cleaning old builds"
    rm -fr $DIST
fi

# invoke packaging
echo "Running package script"
cd ..
python ./scripts/package_app.py
cd $OLDPWD

# Open SSH Proxy
REMOTE_USER=ubuntu
JUMPHOST_KEYS=./fabric_bastion_host_connection
JUMPHOST=18.132.248.142
REMOTE_KEYS=fabric_deploy_keys

DISTRO=$(ls -t $DIST | head -n 1)
FOLDERNAME=$(echo $DISTRO | tr '.' '\n' | head -n 1)

for server in '35.176.160.133'; do
    echo "\n Copying distro $DISTRO to $server"
    scp -r -i $REMOTE_KEYS ../dist/$DISTRO $REMOTE_USER@$server:/tmp

    echo "Unzipping $FOLDERNAME"
    ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
    "unzip /tmp/$DISTRO -d /var/www/zenteach_be/$FOLDERNAME"


    echo "Removing current symbolic link"
    ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
    "rm /var/www/zenteach_be/zenteach"

    echo "Recreating Symbolic link"
    ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
    "ln -s /var/www/zenteach_be/$FOLDERNAME /var/www/zenteach_be/zenteach"

    echo "Cleaning up tmp"
    ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
    "rm -r /tmp/$DISTRO"
    
    echo "Run migrations"
    ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
    "cd /var/www/zenteach_be/zenteach && source ./entrypoint_prod.sh"

    echo "Copy configuration to instance file"
    ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
    "cd /var/www/zenteach_be && mkdir zenteach/instance && cp /var/www/zenteach_be/application.cfg zenteach/instance/"

    ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
    "sudo supervisorctl restart zenteach_be zenteach_celery_processor"
done
