properties([parameters([string('WORKER_IMAGE_NAME')])])

pipeline {
    agent {
        docker {
        label 'jenkins-general-docker'
        image '352708296901.dkr.ecr.eu-central-1.amazonaws.com/itay-jenkins:1'
        args  '--user root -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        APP_ENV = "dev"
    }

//     parameters {
//         string(name: 'WORKER_IMAGE_NAME')
//     }

    stages {
        stage('WorkerDeploy') {
            steps {
                withCredentials([
                    file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
                ]) {
                    sh '''
                    K8S_CONFIGS=infra/k8s

                    # replace placeholders in YAML k8s files
                    bash common/replaceInFile.sh $K8S_CONFIGS/worker.yaml APP_ENV $APP_ENV
                    bash common/replaceInFile.sh $K8S_CONFIGS/worker.yaml WORKER_IMAGE $WORKER_IMAGE_NAME

                    # apply the configurations to k8s cluster
                    kubectl apply --kubeconfig ${KUBECONFIG} -f $K8S_CONFIGS/worker.yaml
                    '''
                }
            }
        }
    }
}