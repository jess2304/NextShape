pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Test') {
            steps {
                sh 'docker compose -p nextshape-ci-${BUILD_NUMBER} -f docker-compose.ci.yml up --build --abort-on-container-exit --exit-code-from app'
            }
        }
    }

    post {
        always {
            sh 'docker compose -p nextshape-ci-${BUILD_NUMBER} -f docker-compose.ci.yml down -v --remove-orphans'
        }
    }
}
