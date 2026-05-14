pipeline {
    agent any

    options {
        timestamps()
    }
    environment {
        COMPOSE_PROJECT_NAME = "nextshape-ci-${BUILD_NUMBER}"
        IMAGE_TAG = "${GIT_COMMIT}"
        REGISTERY = "ghcr.io"
        REGISTERY_IMAGE = "ghcr.io/jess2304/NextShape/nextshape-app"
    }
    stages {

        stage('Validate Compose') {
            steps {
                sh 'docker compose -f docker-compose.ci.yml config --quiet'
            }
        }
        stage('Audit Frontend Dependencies') {
            steps {
                sh 'docker run --rm -v "$PWD/UI:/app" -w /app node:20-alpine npm audit --omit=dev --audit-level=high'
            }
        }
        stage('Audit Backend Dependencies') {
            steps {
                sh 'docker run --rm -v "$PWD/WS:/app" -w /app python:3.11-slim sh -c "pip install --no-cache-dir pip-audit && pip-audit -r requirements.txt"'
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
        stage('Login to GitHub Container Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'ghcr-credentials', usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_TOKEN')]) {
                    sh 'echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USER}" --password-stdin'
                }
            }
        }
        stage('Push Production Image to Registry') {
            steps {
                sh 'docker tag nextshape-app:${IMAGE_TAG} ${REGISTERY_IMAGE}:${IMAGE_TAG}'
                sh 'docker push ${REGISTERY_IMAGE}:${IMAGE_TAG}'
            }
        }
        stage('Write Build Metadata') {
            steps {
                sh '''
                mkdir -p build-metadata
                echo "IMAGE_NAME=nextshape-app" > build-metadata/image.env
                echo "IMAGE_TAG=${IMAGE_TAG}" >> build-metadata/image.env
                echo "GIT_COMMIT=${GIT_COMMIT}" >> build-metadata/image.env
                echo "BUILD_NUMBER=${BUILD_NUMBER}" >> build-metadata/image.env
                echo "BUILD_URL=${BUILD_URL}" >> build-metadata/image.env
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'test-results/*.xml'
            archiveArtifacts artifacts: 'test-results/*.xml', allowEmptyArchive: true
            archiveArtifacts artifacts: 'build-metadata/*.env', allowEmptyArchive: true
            sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.ci.yml down -v --remove-orphans'
        }
    }
}
