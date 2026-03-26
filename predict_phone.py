import numpy as np
import pandas as pd
import mlflow

# 1) MLflow setup
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("smartphones-price-prediction")

# 2) Chargement du modèle
model_uri = "models:/smartphones_price_model/latest"
model = mlflow.pyfunc.load_model(model_uri)

# 3) Charger les colonnes sauvegardées lors du train
feature_columns = pd.read_csv("feature_columns.csv").squeeze().tolist()

# 4) Tes smartphones à prédire (format brut, comme le CSV original)
data_raw = [
    {
        "Brand": "Samsung", "Model": "Galaxy M23", "RAM": 4, "Storage": 128,
        "Color": "Blue", "Free": "Yes"
    },
    {
        "Brand": "Xiaomi", "Model": "Redmi Note 11S", "RAM": 6, "Storage": 128,
        "Color": "Gray", "Free": "Yes"
    },
    {
        "Brand": "Motorola", "Model": "Moto G13", "RAM": 4, "Storage": 128,
        "Color": "Blue", "Free": "Yes"
    },
]

df_predict = pd.DataFrame(data_raw)

# 5) Même preprocessing que train.py
df_predict["Free"] = df_predict["Free"].map({"Yes": 1, "No": 0})
df_predict = pd.get_dummies(df_predict, columns=["Brand", "Model", "Color"], drop_first=True)

# Aligner les colonnes exactement comme X_train
df_predict = df_predict.reindex(columns=feature_columns, fill_value=0)

# 6) Run MLflow
with mlflow.start_run(run_name="batch_predict_smartphones") as run:
    pred = model.predict(df_predict)

    mlflow.log_param("model_uri", model_uri)
    mlflow.log_metric("n_rows",    int(len(df_predict)))
    mlflow.log_metric("pred_mean", float(np.mean(pred)))
    mlflow.log_metric("pred_min",  float(np.min(pred)))
    mlflow.log_metric("pred_max",  float(np.max(pred)))

    out = df_predict.copy()
    out["predicted_price"] = pred
    out.to_csv("predictions.csv", index=False)
    mlflow.log_artifact("predictions.csv")

    print("Run ID predict :", run.info.run_id)

for i, (p, row) in enumerate(zip(pred, data_raw)):
    print(f"Smartphone {i+1} ({row['Brand']} {row['Model']}) → Prix prédit : {p:.2f} €")