pipeline {
    agent any

    options {
        timestamps()
    }
    environment {
        COMPOSE_PROJECT_NAME = "nextshape-ci-${BUILD_NUMBER}"
        IMAGE_TAG = "${GIT_COMMIT}"
    }
    stages {

        stage('Validate Compose') {
            steps {
                sh 'docker compose -f docker-compose.ci.yml config --quiet'
            }
        }
        stage('Audit Frontend Dependencies') {
            steps {
                sh 'docker run --rm -v "$PWD/UI:/app" -w /app node:20-alpine npm audit --audit-level=high'
            }
        }
        stage('Build Test Image') {
            steps {
                sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.ci.yml build'
            }
        }
        stage('Prepare Test Reports') {
            steps {
                sh 'rm -rf test-results && mkdir -p test-results'
            }
        }
        stage('Run Backend Tests') {
            steps {
                sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.ci.yml up --abort-on-container-exit --exit-code-from app'
            }
        }
        stage('Build Production Image') {
            steps {
                sh 'docker build --target production --build-arg VITE_API_URL=http://localhost:8000/api/ -t nextshape-app:${IMAGE_TAG} -f WS/Dockerfile .'
            }
        }
        stage('Scan Production Image') {
            steps {
                sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --ignore-unfixed --exit-code 1 --severity HIGH,CRITICAL nextshape-app:${IMAGE_TAG}'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'test-results/*.xml'
            sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.ci.yml down -v --remove-orphans'
        }
    }
}
