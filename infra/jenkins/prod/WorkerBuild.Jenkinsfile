pipeline {
    agent {
        docker {
        label 'jenkins-general-docker'
        image '352708296901.dkr.ecr.eu-central-1.amazonaws.com/itay-jenkins'
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
    IMAGE_NAME = "itay-worker"
    WORKSPACE = "/home/ec2-user/workspace/prod/WorkerBuild/"
    }

    stages {
        stage('WorkerBuild') {
            steps {

                sh '''
                aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin $REGISTRY_URL
                ls
                pwd
                cd $WORKSPACE
                docker build -t $IMAGE_NAME:$IMAGE_TAG . -f services/worker/Dockerfile

                '''
            }
        }

    stage('Snyx Check') {
    steps {
            withCredentials([string(credentialsId: 'Snyx', variable: 'SNYK_TOKEN')]) {
                sh 'snyk container test $IMAGE_NAME:$IMAGE_TAG --severity-threshold=critical --file=/home/ec2-user/workspace/prod/WorkerBuild/services/worker/Dockerfile'
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

        stage('Trigger WorkerDeploy') {
            steps {
                build job: 'WorkerDeploy', wait: false, parameters: [
                    string(name: 'WORKER_IMAGE_NAME', value: "${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}")
                ]
            }
        }
    }
}