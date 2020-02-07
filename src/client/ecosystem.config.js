module.exports = {
  apps : [{
    name: 'Zenteach client',
    script: 'main.js',

    // Options reference: https://pm2.keymetrics.io/docs/usage/application-declaration/
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development'
    },
    env_production: {
      NODE_ENV: 'production'
    }
  }],

  deploy : {
    "production" : {
			"user" : "ubuntu",
			"key"  : "/Users/natnaelgetahun/.ssh/stage_server.pem",
			"host" : ["3.8.120.67"],
			"ref"  : "origin/master",
			"repo" : "git@github.com:ngetahun/zenteach.git",
			"ssh_options": "StrictHostKeyChecking=no",
			"path" : "/var/www/portal.zenteach.co.uk",
			"post-deploy" : "yarn install; yarn build; yarn serve; pm2 startOrRestart ecosystem.json --env production"
		},
		"stage": {
			"user" : "root",
			"key"  : "/Users/natnaelgetahun/.ssh/id_rsa.pub",
			"host" : ["67.207.76.204"],
			"ref"  : "origin/master",
			"repo" : "git@github.com:ngetahun/zenteach.git",
			"ssh_options": ["StrictHostKeyChecking=no", "ForwardAgent=yes"],
			"path" : "/var/www/stage.portal.zenteach.co.uk",
			"post-deploy" : "yarn install; yarn build; yarn serve; pm2 startOrRestart ecosystem.json --env stage"

		 }
	},
};
