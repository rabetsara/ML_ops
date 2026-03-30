pipeline {
    agent any

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
                    mkdir -p ${WORKSPACE}/trivy-reports

                    # Étape 1 : Scan Trivy → JSON
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v $HOME/.cache/trivy:/root/.cache/trivy \
                        -v ${WORKSPACE}/trivy-reports:/reports \
                        aquasec/trivy:0.69.3 image \
                        --exit-code 0 \
                        --severity HIGH,CRITICAL \
                        --format json \
                        --output /reports/trivy-raw.json \
                        smartphones-ml-app

                    # Étape 2 : JSON → CSV dans le même conteneur Trivy
                    docker run --rm \
                        -v ${WORKSPACE}/trivy-reports:/reports \
                        aquasec/trivy:0.69.3 \
                        sh -c "python3 -c \"
import json, csv

with open('/reports/trivy-raw.json') as f:
    data = json.load(f)

rows = []
for result in data.get('Results', []):
    for vuln in result.get('Vulnerabilities', []):
        rows.append([
            vuln.get('PkgName', ''),
            vuln.get('VulnerabilityID', ''),
            vuln.get('Severity', ''),
            vuln.get('InstalledVersion', ''),
            vuln.get('FixedVersion', ''),
            vuln.get('Title', '').replace(',', ' ')
        ])

with open('/reports/resultat.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['PackageName','VulnerabilityID','Severity','InstalledVersion','FixedVersion','Title'])
    writer.writerows(rows)

print(str(len(rows)) + ' vulnerabilites ecrites dans resultat.csv')
\""

                    echo "--- Aperçu du rapport ---"
                    head -20 ${WORKSPACE}/trivy-reports/resultat.csv
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
                    echo "Impossible d'arrêter les services : ${e.message}"
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
