pipeline {
    agent any

    environment {
        EC2_HOST = 'ec2-user@13.59.87.182'
        APP_DIR = '/home/ec2-user/django_site2'
    }

    stages {
        stage('Clone repo') {
            steps {
                echo "Starting repository clone..."
                git branch: 'main', url: 'https://github.com/JBuxo/django-polling.git'
                echo "Repository clone completed"
            }
        }

        stage('Test SSH Connection') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                    echo "Testing SSH connection to EC2 instance..."
                    ssh -o StrictHostKeyChecking=no $EC2_HOST 'echo "SSH connection successful"'
                    """
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                    echo "Creating application directory on EC2..."
                    ssh -o StrictHostKeyChecking=no $EC2_HOST 'mkdir -p $APP_DIR'
                    
                    echo "Copying files to EC2..."
                    scp -o StrictHostKeyChecking=no -r . $EC2_HOST:$APP_DIR/ || (echo "SCP failed with exit code: \$?" && exit 1)
                    
                    echo "Verifying files were copied..."
                    ssh -o StrictHostKeyChecking=no $EC2_HOST 'ls -la $APP_DIR'
                    """
                }
            }
        }

        stage('Run Django App') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                    echo "Starting Django application deployment..."
                    ssh -o StrictHostKeyChecking=no $EC2_HOST << 'EOF'
                      set -e  # Exit immediately if a command exits with a non-zero status
                      cd $APP_DIR
                      echo "Creating virtual environment..."
                      python3 -m venv venv || (echo "Failed to create virtual environment" && exit 1)
                      
                      echo "Activating virtual environment..."
                      source venv/bin/activate
                      
                      echo "Upgrading pip..."
                      pip install --upgrade pip
                      
                      echo "Installing dependencies..."
                      pip install -r requirements.txt
                      
                      echo "Running database migrations..."
                      python manage.py migrate
                      
                      echo "Checking if Django is already running..."
                      pkill -f "python manage.py runserver" || echo "No existing Django process found"
                      
                      echo "Starting Django server..."
                      nohup python manage.py runserver 0.0.0.0:81 > django.log 2>&1 &
                      
                      echo "Waiting for server to start..."
                      sleep 5
                      
                      echo "Checking if server is running..."
                      ps aux | grep "runserver" | grep -v grep
                      
                      echo "Django deployment completed"
                    EOF
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed'
        }
        success {
            echo 'Pipeline executed successfully'
        }
        failure {
            echo 'Pipeline execution failed'
            sshagent(credentials: ['ec2-ssh-key']) {
                sh """
                echo "Fetching logs from EC2 instance..."
                ssh -o StrictHostKeyChecking=no $EC2_HOST 'cat $APP_DIR/django.log || echo "Log file not found"'
                """
            }
        }
    }
}