pipeline {
    agent any

    environment {
        EC2_USER = 'ec2-user'
        EC2_HOST = '13.59.87.182'
        PROJECT_PATH = '/home/ec2-user/new_project'
        SSH_KEY = credentials('ec2-ssh-key')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo 'Deploying to EC2 server...'
                sh """
                ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << 'EOF'
                    if [ ! -d "${PROJECT_PATH}" ]; then
                        mkdir -p ${PROJECT_PATH}
                        git clone https://github.com/JBuxo/django-polling.git ${PROJECT_PATH}
                    else
                        cd ${PROJECT_PATH}
                        git pull origin main
                    fi
                    # Optional: Run build/start commands here
                    # npm install
                    # pm2 restart app
                    # systemctl restart nginx
                EOF
                """
            }
        }
    }

    post {
        success {
            echo 'success'
        }
        failure {
            echo 'failure'
        }
    }
}
