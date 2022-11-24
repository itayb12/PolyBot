pipeline {
    agent {
        docker {
        label 'jenkins-general-docker-itay'
        image '352708296901.dkr.ecr.eu-central-1.amazonaws.com/itay-jenkins:1'
        args  '--user root -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    options {
    buildDiscarder(logRotator(daysToKeepStr: '30'))
    disableConcurrentBuilds()
    timestamps()
    }

    environment {
    REGISTRY_URL = "352708296901.dkr.ecr.eu-central-1.amazonaws.com"
    IMAGE_TAG = "0.0.$BUILD_NUMBER"
    IMAGE_NAME = "itay-bot"
    WORKSPACE = "/home/ec2-user/workspace/prod/BotBuild/"
    }

    stages {
        stage('Build') {
            steps {
                sh '''
                aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin $REGISTRY_URL
                cd $WORKSPACE
                docker build -t $IMAGE_NAME:$IMAGE_TAG . -f services/bot/Dockerfile
                '''
            }
        }

        stage('Snyx Check') {
            steps {
                withCredentials([string(credentialsId: 'Snyx', variable: 'SNYK_TOKEN')]) {
                    sh 'snyk container test $IMAGE_NAME:$IMAGE_TAG --severity-threshold=critical --file=/home/ec2-user/workspace/prod/BotBuild/services/bot/Dockerfile'
                }
            }
        }

        stage('Continue_Build') {
            steps {
                sh'''
                docker tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY_URL/$IMAGE_NAME:$IMAGE_TAG
                docker push $REGISTRY_URL/$IMAGE_NAME:$IMAGE_TAG
                '''
            }
            post {
                always {
                sh '''
                docker image prune -a --filter "until=24h"
                '''
                }
            }
        }

        stage('Trigger Deploy') {
            steps {
                build job: 'BotDeploy', wait: false, parameters: [
                    string(name: 'BOT_IMAGE_NAME', value: "${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}")
                ]
            }
        }
    }
}