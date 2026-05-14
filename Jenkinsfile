// pipeline {
//     agent any

//     environment {
//         IMAGE_NAME = "codered-api"
//         DOCKER_HUB_REPO = "yourdockerhubusername/codered-api"
//     }

//     stages {

//         stage('Checkout') {
//             steps {
//                 echo 'Pulling code from GitHub...'
//                 checkout scm
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 echo 'Building Docker image...'
//                 sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
//                 sh "docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${DOCKER_HUB_REPO}:${BUILD_NUMBER}"
//                 sh "docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${DOCKER_HUB_REPO}:latest"
//             }
//         }

//         stage('Push to Docker Hub') {
//             steps {
//                 echo 'Pushing image to Docker Hub...'
//                 withCredentials([usernamePassword(
//                     credentialsId: 'dockerhub-creds',
//                     usernameVariable: 'DOCKER_USER',
//                     passwordVariable: 'DOCKER_PASS'
//                 )]) {
//                     sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
//                     sh "docker push ${DOCKER_HUB_REPO}:${BUILD_NUMBER}"
//                     sh "docker push ${DOCKER_HUB_REPO}:latest"
//                 }
//             }
//         }

//         stage('Deploy to Kubernetes') {
//             steps {
//                 echo 'Deploying to Minikube...'
//                 sh "kubectl set image deployment/codered-api codered-api=${DOCKER_HUB_REPO}:${BUILD_NUMBER}"
//                 sh "kubectl rollout status deployment/codered-api"
//             }
//         }
//     }

//     post {
//         success {
//             echo 'Pipeline completed successfully!'
//         }
//         failure {
//             echo 'Pipeline failed!'
//         }
//     }
// }

pipeline {
    agent any

    stages {
        stage('Pre-Build') {
            steps {
                echo 'Pre-Build...'
                echo 'Send status Pre-Build to Mail, Telegram, Slack...'
            }
        }
        stage('Build') {
            steps {
                echo 'Building...'
                echo 'Running docker build...'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Push') {
            steps {
                echo 'Pushing...'
                echo 'Running docker push...'
            }
        }
    }
    
    post {
        success {
            echo 'Success...'
            echo 'Send status Success to Mail, Telegram, Slack...'
        }
        failure {
            echo 'Failure...'
            echo 'Send status Failure to Mail, Telegram, Slack...'
        }
    }

}