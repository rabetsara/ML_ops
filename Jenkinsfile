pipeline {
    agent any

    stages {
        stage('Cleanup') {
            steps {
                echo "Nettoyage des anciens conteneurs..."
                sh 'docker-compose down --remove-orphans || true'
            }
        }

        stage('Build Image') {
            steps {
                echo "Construction de l'image de l'application..."
                // On build via compose pour s'assurer que les tags correspondent
                sh 'docker-compose build app'
            }
        }

        stage('Start MLflow') {
            steps {
                echo "Démarrage de MLflow..."
                sh 'docker-compose up -d mlflow'
                echo "Attente du démarrage (20 secondes)..."
                sleep 20
            }
        }

        stage('Model Training') {
            steps {
                echo "Lancement de l'entraînement..."
                // Utilisation impérative de docker-compose run pour hériter du DNS
                sh 'docker-compose run --rm app python train_phone.py'
            }
        }

        stage('Model Validation') {
            steps {
                echo "Lancement de la prédiction..."
                sh 'docker-compose run --rm app python predict_phone.py'
            }
        }
    }

    post {
        always {
            echo "Arrêt des services..."
            sh 'docker-compose stop'
        }
    }
}
