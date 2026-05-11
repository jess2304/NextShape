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
        stage('Build Image') {
            steps {
                sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.ci.yml build'
            }
        }
        stage('Scan Image') {
            steps {
                sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL nextshape-app:${IMAGE_TAG}'
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
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'test-results/*.xml'
            sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.ci.yml down -v --remove-orphans'
        }
    }
}
