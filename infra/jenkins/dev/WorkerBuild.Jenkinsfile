pipeline {
    agent {
        docker {
        label 'jenkins-general-docker'
        image '352708296901.dkr.ecr.eu-west-1.amazonaws.com/zoharn-jenkins-agent:1'
        args  '--user root -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    options {
    buildDiscarder(logRotator(daysToKeepStr: '30'))
    disableConcurrentBuilds()
    timestamps()

    }

    environment {
    REGISTRY_URL = "352708296901.dkr.ecr.eu-west-1.amazonaws.com"
    IMAGE_TAG = "0.0.$BUILD_NUMBER"
    IMAGE_NAME = "zoharn007-worker"
    WORKSPACE = "/var/lib/jenkins/workspace/workerBuild/services"

    }

    stages {
        stage('workerBuild') {
            steps {

                sh '''
                aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin $REGISTRY_URL
                cd /home/ec2-user/workspace/dev/WorkerBuild/services/worker/
                docker build -t $IMAGE_NAME:$IMAGE_TAG .

                '''
            }
        }

    stage('Snyx Check') {
    steps {
            withCredentials([string(credentialsId: 'Snyx', variable: 'SNYK_TOKEN')]) {
                sh 'snyk container test $IMAGE_NAME:$IMAGE_TAG --severity-threshold=critical --file=/home/ec2-user/workspace/dev/WorkerBuild/services/bot/Dockerfile'
            }
        }
    }

    stage('Continue_workerBuild') {
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

        stage('Trigger workerDeploy') {
            steps {
                build job: 'workerDeploy', wait: false, parameters: [
                    string(name: 'WORKER_IMAGE_NAME', value: "${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}")
                ]
            }
        }
    }
}