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

                sh 'mkdir -p ${WORKSPACE}/trivy-reports'

                writeFile file: 'trivy-reports/csv.tpl', text: '''PackageName,VulnerabilityID,Severity,InstalledVersion,FixedVersion,Title
{{- range . }}
{{- range .Vulnerabilities }}
{{ .PkgName }},{{ .VulnerabilityID }},{{ .Severity }},{{ .InstalledVersion }},{{ .FixedVersion }},{{ .Title | js }}
{{- end }}
{{- end }}
'''
                sh '''
                    echo "=== Vérification du template avant scan ==="
                    ls -la ${WORKSPACE}/trivy-reports/
                    cat ${WORKSPACE}/trivy-reports/csv.tpl

                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v $HOME/.cache/trivy:/root/.cache/trivy \
                        -v ${WORKSPACE}/trivy-reports:/reports \
                        aquasec/trivy:0.69.3 image \
                        --exit-code 0 \
                        --severity HIGH,CRITICAL \
                        --format template \
                        --template "@/reports/csv.tpl" \
                        --output /reports/resultat.csv \
                        smartphones-ml-app

                    echo "--- Aperçu du rapport Trivy ---"
                    cat ${WORKSPACE}/trivy-reports/resultat.csv
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
