pipeline {
    agent any

    environment {
        // Nom de l'image de ton application
        DOCKER_IMAGE = "smartphones-ml-app"
    }

    stages {
        stage('Cleanup') {
            steps {
                echo "Nettoyage des anciens conteneurs..."
                sh 'docker-compose down --remove-orphans || true'
            }
        }

        stage('Build Image') {
            steps {
                echo "Construction de l'image Docker de l'application..."
                sh "docker build -t ${DOCKER_IMAGE} ."
            }
        }

        stage('Start MLflow') {
            steps {
                echo "Démarrage du serveur MLflow..."
                sh 'docker-compose up -d mlflow'
                // On attend que le serveur soit prêt (important pour éviter Connection Refused)
                echo "Attente du démarrage (20 secondes)..."
                sleep 20
            }
        }

        stage('Model Training') {
            steps {
                echo "Lancement de l'entraînement du modèle..."
                // On utilise 'run' pour que le script s'exécute dans le réseau du compose
                sh 'docker-compose run --rm app python train_phone.py'
            }
        }

        stage('Model Validation') {
            steps {
                echo "Test de prédiction..."
                sh 'docker-compose run --rm app python predict_phone.py'
            }
        }
    }

    post {
        always {
            echo "Arrêt des services..."
            sh 'docker-compose stop'
        }
        success {
            echo "Pipeline terminé avec succès !"
        }
        failure {
            echo "Le pipeline a échoué. Vérifiez les logs."
        }
    }
}
