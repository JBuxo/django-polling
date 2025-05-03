pipeline {
    agent any

    environment {
        EC2_HOST = 'ec2-user@13.59.87.182'
        APP_DIR = '/home/ec2-user/django_site2'
    }

    stages {

        stage('Clone repo') {
            steps {
                git branch: 'main', url: 'https://github.com/JBuxo/django-polling.git'
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no $EC2_HOST 'mkdir -p $APP_DIR'
                    scp -o StrictHostKeyChecking=no -r . $EC2_HOST:$APP_DIR/
                    """
                }
            }
        }

        stage('Run Django App') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no $EC2_HOST << 'EOF'
                      cd $APP_DIR
                      python3 -m venv venv
                      source venv/bin/activate
                      pip install --upgrade pip
                      pip install -r requirements.txt
                      python manage.py migrate
                      nohup python manage.py runserver 0.0.0.0:81 > django.log 2>&1 &
                    EOF
                    """
                }
            }
        }
    }
}