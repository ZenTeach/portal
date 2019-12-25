pipeline {
  agent any
  stages {
    stage('Clone Project') {
      steps {
        ws(dir: '/home/build')
        sh 'git clone git@github.com:philippmikio/zenteach.git'
        dir(path: '/home/builds')
      }
    }

    stage('Start Build Frontend Build') {
      agent {
        docker {
          image 'node:10.16-alpine'
        }

      }
      steps {
        dir(path: '/home/build/zenteach/src/client')
        echo 'Installing Packages'
        sh 'yarn install'
        echo 'Running Unit tests'
        sh 'yarn run test:unit'
        echo 'Building project'
        sh 'yarn run build'
        sh 'tar -czf dist.tar.gz ./dist'
        echo 'Compressing dist files'
        sh 'tar -czf dist.tar.gz ./dist'
        archiveArtifacts(artifacts: 'dist.tar.gz', fingerprint: true)
      }
    }

  }
}