pipeline {
  agent any
  environment {
        CI = 'true'
  }
  stages {
    stage('Clone Project') {
      steps {
        ws(dir: '/home/builds')
        sh 'git clone git@github.com:ngetahun/zenteach.git'
        dir(path: '/home/builds')
      }
    }

		
    // Build FE
    stage("Build Frontend Project") {
      when {
        changeset '**/client/*.*'
      }
      agent {
        docker {
          image 'node:10.16-alpine'
        }
      }

      steps {
        dir('client/') {
          echo 'Installing Packages'
          sh 'yarn install'
          echo 'Running Unit tests'
          sh 'yarn run test:unit'
          echo 'Building project'
          sh 'yarn run build'
          echo 'Compressing dist files'
          sh 'tar -czf dist_${BUILD_NUMBER}.tar.gz ./dist'
          archiveArtifacts(artifacts: 'dist_${BUILD_NUMBER}.tar.gz', fingerprint: true)
          echo 'Copying artifacts to S3'
        }

      }

    }

    // Build Backend
    stage('Start Build Frontend Build') {
      when {
        changeset '**/backend/*.*'
      }
      agent {
        docker {
          image 'python:3.7.2-alpine'
        }
      }

      steps {
        dir('backend/')
      }

    }

  }

	// TODO: Write gradle scripts to build both projects
}
