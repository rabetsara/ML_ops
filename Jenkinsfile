pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "smartphones-ml-app"
    }

    stages {
        stage('Checkout') {
            steps {
                // Récupération du code depuis GitHub (déjà configuré par ton lien Git)
                checkout scm
            }
        }

        stage('Build Image') {
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE} ."
                }
            }
        }

        stage('Start MLflow') {
            steps {
                // On lance MLflow en arrière-plan s'il n'est pas déjà là
                sh "docker-compose up -d mlflow"
            }
        }

        stage('Training & Logging') {
            steps {
                script {
                    // On exécute l'entraînement à l'intérieur du conteneur
                    // On utilise le réseau de docker-compose pour parler à MLflow
                    sh "docker-compose run --rm training-app python train_phone.py"
                }
            }
        }

        stage('Model Validation') {
            steps {
                script {
                    // Test de la prédiction avec les données de batch
                    sh "docker-compose run --rm training-app python predict_phone.py"
                }
            }
        }
    }

    post {
        always {
            // Nettoyage des conteneurs de run, mais on garde MLflow
            sh "docker-compose stop"
        }
        success {
            echo "Pipeline terminé avec succès ! Le modèle est disponible sur MLflow (port 5000)."
        }
    }
}