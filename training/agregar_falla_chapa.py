import pandas as pd
import os
import subprocess

# Cargar dataset existente
ruta_csv = "data/dataset_sintomas.csv"
if os.path.exists(ruta_csv):
    df = pd.read_csv(ruta_csv)
else:
    df = pd.DataFrame(columns=["sintoma", "falla"])

# Nuevos síntomas específicos para la chapa de la puerta y cierre mecánico
nuevos_datos = [
    {"sintoma": "pasa que al cerrar la puerta de mi auto y al aplastar el control de la puerta este no lo abre y sigue bloqueada", "falla": "Daño o desalineacion en la chapa / mecanismo de seguro de la puerta"},
    {"sintoma": "la chapa de la puerta esta inclinada para el costado y no abre", "falla": "Daño o desalineacion en la chapa / mecanismo de seguro de la puerta"},
    {"sintoma": "el seguro mecanico de la puerta se quedo trabado o chueco", "falla": "Daño o desalineacion en la chapa / mecanismo de seguro de la puerta"},
    {"sintoma": "la chapa de la puerta no encaja ni cierra bien", "falla": "Daño o desalineacion en la chapa / mecanismo de seguro de la puerta"},
    {"sintoma": "el pestillo de la puerta esta doblado y la chapa no responde", "falla": "Daño o desalineacion en la chapa / mecanismo de seguro de la puerta"},
    {"sintoma": "la cerradura de la puerta se quedo trabada hacia un lado", "falla": "Daño o desalineacion en la chapa / mecanismo de seguro de la puerta"},
    {"sintoma": "aplasto el control y el seguro de la puerta se queda trabado", "falla": "Daño o desalineacion en la chapa / mecanismo de seguro de la puerta"}
]

df_nuevos = pd.DataFrame(nuevos_datos)
df_final = pd.concat([df, df_nuevos], ignore_index=True)
df_final.drop_duplicates(subset=['sintoma'], inplace=True)
df_final.to_csv(ruta_csv, index=False, encoding="utf-8")

print(f"¡Nuevos síntomas de 'Chapa de puerta' agregados con éxito! Total dataset: {len(df_final)} muestras.")

# Re-entrenar modelo
print("Re-entrenando el modelo de Machine Learning...")
subprocess.run(["python", "training/entrenar_modelo.py"])
