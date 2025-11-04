cat > Jenkinsfile << 'EOF'
pipeline {
  agent any

  environment {
    REGISTRY = 'docker.io'
    IMAGE_REPO = 'mrcarpediem/flask-mysql-demo'
    APP_TAG = "${env.BUILD_NUMBER}"
    LATEST_TAG = 'latest'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Image') {
      steps {
        sh '''
          docker build -t ${IMAGE_REPO}:${APP_TAG} -t ${IMAGE_REPO}:${LATEST_TAG} ./web
        '''
      }
    }

    stage('Test Container') {
      steps {
        sh '''
          docker rm -f test-db test-app || true
          docker network create ci-net || true

          docker run -d --name test-db --network ci-net \
            -e MYSQL_ROOT_PASSWORD=rootpass \
            -e MYSQL_DATABASE=appdb \
            -e MYSQL_USER=appuser \
            -e MYSQL_PASSWORD=apppass \
            mysql:8.0

          echo "Waiting for DB..."
          for i in {1..30}; do docker exec test-db mysqladmin ping -prootpass --silent && break; sleep 2; done

          docker run -d --name test-app --network ci-net \
            -e MYSQL_HOST=test-db \
            -e MYSQL_USER=appuser \
            -e MYSQL_PASSWORD=apppass \
            -e MYSQL_DATABASE=appdb \
            -p 5001:5000 ${IMAGE_REPO}:${LATEST_TAG}

          for i in {1..30}; do curl -sf http://localhost:5001/health && break; sleep 2; done
          docker rm -f test-app test-db
          docker network rm ci-net
        '''
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
          sh '''
            echo "$PASS" | docker login -u "$USER" --password-stdin ${REGISTRY}
            docker push ${IMAGE_REPO}:${APP_TAG}
            docker push ${IMAGE_REPO}:${LATEST_TAG}
          '''
        }
      }
    }
  }

  post {
    always {
      sh 'docker image prune -f || true'
    }
  }
}
EOF
