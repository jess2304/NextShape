pipeline {
    agent any

    options {
        timestamps()
    }
    environment {
        COMPOSE_PROJECT_NAME = "nextshape-ci-${BUILD_NUMBER}"
    }
    stages {

        stage('Validate Compose') {
            steps {
                sh 'docker compose -f docker-compose.ci.yml config --quiet'
            }
        }
        stage('Build Images') {
            steps {
                sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.ci.yml build'
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
            sh 'docker compose -p ${COMPOSE_PROJECT_NAME} -f docker-compose.ci.yml down -v --remove-orphans'
        }
    }
}
