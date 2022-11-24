pipeline {
    agent {
        docker {
        label 'jenkins-general-docker-itay'
        image '352708296901.dkr.ecr.eu-central-1.amazonaws.com/itay-jenkins:1'
        args  '--user root -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    stages {
        stage('Unittest Bot') {
            steps {
                echo 'testing bot...'
            }
        }
        stage('Unittest Worker') {
            steps {
                echo 'testing worker...'
            }
        }
        stage('Linting test') {
            steps {
              echo 'code linting'
            }
        }
    }
}