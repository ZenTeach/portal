#!/usr/bin/env bash
set -euo pipefail

DIST='../dist'

if [[ -d $DIST ]]; then
    echo "Cleaning old builds"
    rm -fr $DIST 2> /dev/null || true
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
REMOTE_KEYS=./fabric_deploy_keys

chmod 400 $JUMPHOST_KEYS && chmod 400 $REMOTE_KEYS

DISTRO=$(ls -t $DIST | head -n 1)
FOLDERNAME=$(echo $DISTRO | tr '.' '\n' | head -n 1)

server=`echo $SERVER_NAME`

echo "Performing clean up. Leaving only last 5 builds."
ssh -i $REMOTE_KEYS $REMOTE_USER@$server -o StrictHostKeyChecking=no \
"ls -lt /var/www/zenteach_be/ | grep -E 'zenteach-build-*' | tail -n +7 | awk '{print \$9}' | xargs -I {} rm -fr /var/www/zenteach_be/{} 2> /dev/null || true"


echo "\n Copying distro $DISTRO to $server"
scp -r -i $REMOTE_KEYS -o "StrictHostKeyChecking=no" ../dist/$DISTRO $REMOTE_USER@$server:/tmp

echo "Unzipping $FOLDERNAME"
ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
-o "StrictHostKeyChecking=no" \
"unzip /tmp/$DISTRO -d /var/www/zenteach_be/$FOLDERNAME"


echo "Removing current symbolic link"
ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
-o "StrictHostKeyChecking=no" \
"rm /var/www/zenteach_be/zenteach 2> /dev/null || true"

echo "Recreating Symbolic link"
ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
-o "StrictHostKeyChecking=no" \
"ln -s /var/www/zenteach_be/$FOLDERNAME /var/www/zenteach_be/zenteach"

echo "Cleaning up tmp"
ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
-o "StrictHostKeyChecking=no"  \
"rm -r /tmp/$DISTRO 2> /dev/null || true"

echo "Run migrations"
ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
-o "StrictHostKeyChecking=no" \
"cd /var/www/zenteach_be/zenteach && source ./entrypoint_prod.sh"

echo "Copy configuration to instance file"
ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
-o "StrictHostKeyChecking=no" \
"cd /var/www/zenteach_be && mkdir zenteach/instance && cp /var/www/zenteach_be/application.cfg zenteach/instance/"

ssh -i $REMOTE_KEYS $REMOTE_USER@$server \
-o "StrictHostKeyChecking=no" \
"sudo systemctl restart zenteach_be zenteach_be_celery zenteach_be_celery_beat"
