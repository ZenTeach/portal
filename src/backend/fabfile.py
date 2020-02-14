from fabric.api import env, local, put, run, cd
from pathlib import Path
env.user = 'ubuntu'
env.hosts = ['35.176.160.133']

def deploy():
    # build the package
    packed_file = local('python ./scripts/package_app.py', capture=True)

    filezip = packed_file.split('-')[2]
    filename = Path(packed_file).stem

    # upload the package to the temporary folder on the server
    put('dist/%s' % packed_file, '/tmp/%s' % packed_file)

    # install the package in the application's virtualenv with pip
    run(f'unzip /tmp/{packed_file} -d /var/www/zenteach_be/{filename}')

    # delete current link
    run('rm /var/www/zenteach_be/zenteach')

    # use current to create a symbolic link
    run(f'ln -s /var/www/zenteach_be/{filename} /var/www/zenteach_be/zenteach')

    # remove the uploaded package
    run(f'rm -r /tmp/{packed_file}')

    # Run migrations and etc..
    with cd("/var/www/zenteach_be/zenteach"):
        run('source ./entrypoint_prod.sh')

    # copy configuration to instance file
    with cd("/var/www/zenteach_be"):
        run("mkdir zenteach/instance")
        run("cp /var/www/zenteach_be/application.cfg zenteach/instance/")

    # touch the .wsgi file to trigger a reload in mod_wsgi
    run('sudo supervisorctl restart zenteach_be')
