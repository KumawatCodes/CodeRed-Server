pipeline {
    agent any

    environment {
        IMAGE_NAME     = "codered-api"
        DOCKER_HUB_REPO = "zen1tsu/codered-api"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling code from GitHub...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat "docker build -t %IMAGE_NAME%:%BUILD_NUMBER% ."
                bat "docker tag %IMAGE_NAME%:%BUILD_NUMBER% %DOCKER_HUB_REPO%:%BUILD_NUMBER%"
                bat "docker tag %IMAGE_NAME%:%BUILD_NUMBER% %DOCKER_HUB_REPO%:latest"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
                    bat "docker push %DOCKER_HUB_REPO%:%BUILD_NUMBER%"
                    bat "docker push %DOCKER_HUB_REPO%:latest"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to Minikube...'
                bat "kubectl set image deployment/codered-api codered-api=%DOCKER_HUB_REPO%:%BUILD_NUMBER%"
                bat "kubectl rollout status deployment/codered-api"
            }
        }
    }

    post {
        success {
            echo 'Pipeline SUCCESS - CodeRed deployed!'
        }
        failure {
            echo 'Pipeline FAILED!'
        }
    }
}