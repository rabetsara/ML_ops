pipeline {
    agent any

    environment {
        TRIVY_CACHE = "/tmp/trivy-cache"
        REPORT_DIR  = "${WORKSPACE}/trivy-reports"
    }

    stages {

        stage('Cleanup') {
            steps {
                echo "Nettoyage des anciens conteneurs..."
                sh 'docker-compose down --remove-orphans || true'
                sh 'docker rmi smartphones-ml-app || true'
            }
        }

        stage('Build Image') {
            steps {
                echo "Construction de l'image..."
                sh 'docker-compose build app'
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                echo "Scan de sécurité de l'image avec Trivy..."
                sh '''
                    mkdir -p ${REPORT_DIR}
                    mkdir -p ${TRIVY_CACHE}

                    echo "=== Scan Trivy (JSON) ==="
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v ${TRIVY_CACHE}:/root/.cache/trivy \
                        -v ${REPORT_DIR}:/reports \
                        aquasec/trivy:0.69.3 image \
                        --exit-code 0 \
                        --severity HIGH,CRITICAL \
                        --scanners vuln \
                        --format json \
                        --output /reports/trivy-raw.json \
                        smartphones-ml-app

                    echo "=== Conversion JSON → CSV avec jq ==="
                    docker run --rm \
                        -v ${REPORT_DIR}:/reports \
                        imega/jq \
                        -r '
                          ["PackageName","VulnerabilityID","Severity","InstalledVersion","FixedVersion","Title"],
                          (.Results[]?.Vulnerabilities[]? |
                          [.PkgName, .VulnerabilityID, .Severity, .InstalledVersion, (.FixedVersion // ""), (.Title // "" | gsub(","; " "))])
                          | @csv
                        ' \
                        /reports/trivy-raw.json > ${REPORT_DIR}/resultat.csv

                    echo "--- Aperçu du rapport ---"
                    head -20 ${REPORT_DIR}/resultat.csv
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-reports/resultat.csv',
                                     allowEmptyArchive: true
                }
            }
        }

        stage('Start MLflow') {
            steps {
                echo "Démarrage de MLflow..."
                sh 'docker-compose up -d mlflow'

                echo "Attente du healthcheck MLflow..."
                sh '''
                    for i in $(seq 1 24); do
                        if docker-compose exec -T mlflow curl -sf http://localhost:5000/health; then
                            echo "MLflow est prêt !"
                            exit 0
                        fi
                        echo "Tentative $i/24 - attente 5s..."
                        sleep 5
                    done
                    echo "MLflow n'a pas démarré à temps"
                    exit 1
                '''
            }
        }

        stage('Model Training') {
            steps {
                echo "Lancement de l'entraînement..."
                sh 'docker-compose run --rm train'
            }
        }

        stage('Model Validation') {
            steps {
                echo "Lancement de la prédiction..."
                sh 'docker-compose run --rm predict'
            }
        }
    }

    post {
        always {
            script {
                try {
                    sh 'docker-compose down --remove-orphans || true'
                } catch (Exception e) {
                    echo "Erreur lors de l'arrêt des services : ${e.message}"
                }
            }
        }
        success {
            echo "Pipeline terminé avec succès !"
        }
        failure {
            echo "Pipeline échoué — consultez les logs ci-dessus."
        }
    }
}
