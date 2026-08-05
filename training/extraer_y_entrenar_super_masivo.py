import json
import pandas as pd
import requests
import os
import random
import subprocess

random.seed(2026)

print("=" * 80)
print("EXTRACTOR Y GENERADOR SUPER MASIVO DE DATASETS DE DIAGNÓSTICO VEHICULAR")
print("Alineado 100% con Informe de Tesis UCV 2026 (Carabayllo)")
print("=" * 80)

# Fuentes directas en GitHub
URL_OBD_JSON = "https://raw.githubusercontent.com/mytrile/obd-trouble-codes/master/obd-trouble-codes.json"
URL_OBD_CSV = "https://raw.githubusercontent.com/AustinMurphy/OBD2-Scantool/master/obd2_std_DTCs.csv"

filas_acumuladas = []

# 1. Extracción de OBD JSON
print(f"Descargando de {URL_OBD_JSON}...")
try:
    r1 = requests.get(URL_OBD_JSON, timeout=10)
    if r1.status_code == 200:
        data1 = r1.json()
        print(f"-> {len(data1)} registros recibidos de OBD JSON.")
        for item in data1:
            for cod, desc in item.items():
                filas_acumuladas.append({"sintoma": f"Codigo escaner {cod}: {desc}", "falla": f"Falla de control electronico {cod[:2]}"})
except Exception as e:
    print(f"Error en fuente 1: {e}")

# 2. Extracción de OBD CSV
print(f"Descargando de {URL_OBD_CSV}...")
try:
    r2 = requests.get(URL_OBD_CSV, timeout=10)
    if r2.status_code == 200:
        lines = r2.text.splitlines()
        print(f"-> {len(lines)} lineas recibidas de OBD CSV.")
        for line in lines[1:]:
            parts = line.split(',')
            if len(parts) >= 2:
                cod = parts[0].strip().replace('"', '')
                desc = parts[1].strip().replace('"', '')
                filas_acumuladas.append({"sintoma": f"Falla detectada OBD2 {cod} - {desc}", "falla": f"Averia detectada en sistema {cod[:2]}"})
except Exception as e:
    print(f"Error en fuente 2: {e}")

# 3. Generador Avanzado Sintáctico de Modismos Peruanos (Carabayllo)
modismos_peru = [
    "maestro una consulta", "buenas tardes mecanico", "resulta que mi auto", "tengo un problema con mi caña",
    "en mi vehiculo noto que", "al salir a trabajar en carabayllo", "en la panamericana norte", "al andar a 60 km por hora"
]

fallas_base_tesis = {
    "Pastillas de freno desgastadas": ["chillido agudo al frenar", "ruido de metal feo en la rueda al pisar freno", "chilla el freno al detenerse"],
    "Fuga de liquido de frenos o aire en el sistema": ["pedal de freno esponjoso se hunde al fondo", "no frena casi nada pedal largo", "nivel de liquido de freno bajo"],
    "Bujias desgastadas o gasolina de bajo octanaje (preignicion)": ["motor cascabelea feo en subida", "cascabeleo fuerte al pisar el acelerador", "tiembla el motor y cascabelea"],
    "Bateria descargada o arrancador defectuoso": ["no da arranque solo hace click click", "bateria muerta luces tenues", "girar la llave y no hace nada"],
    "Soportes de motor rotos o inyectores sucios": ["motor tiembla bastante parado en semaforo", "vibracion fuerte en el timon quieto", "motor zapatea en minimo"],
    "Llantas desalineadas, desbalanceadas o deformadas": ["timon tiembla fuerte a mas de 80 km/h", "direccion vibra en la pista", "carro se jala a la derecha"],
    "Juntas homocineticas (palieres) dañadas": ["suena clac clac fuerte al girar el timon", "crujido en la llanta al doblar la esquina", "traqueteo en el palier"],
    "Daño o desalineacion en la chapa / mecanismo de seguro de la puerta": ["la chapa de la puerta esta chueca no abre", "al aplastar el control la puerta sigue bloqueada", "el seguro de la puerta se quedo trabado"]
}

for falla, frases in fallas_base_tesis.items():
    for frase in frases:
        filas_acumuladas.append({"sintoma": frase, "falla": falla})
        for _ in range(25):
            m = random.choice(modismos_peru)
            filas_acumuladas.append({"sintoma": f"{m} {frase}".strip(), "falla": falla})

df_super = pd.DataFrame(filas_acumuladas)
df_super.drop_duplicates(subset=['sintoma'], inplace=True)

# Guardar en dataset principal
ruta_dataset = "data/dataset_sintomas.csv"
if os.path.exists(ruta_dataset):
    df_previo = pd.read_csv(ruta_dataset)
    df_final = pd.concat([df_previo, df_super], ignore_index=True)
else:
    df_final = df_super

df_final.drop_duplicates(subset=['sintoma'], inplace=True)
df_final.to_csv(ruta_dataset, index=False, encoding="utf-8")

print("=" * 80)
print(f"¡DATASET EXTRAÍDO Y INTEGRADO AL 100%!")
print(f"-> Muestras acumuladas totales: {len(df_final)} filas.")
print("=" * 80)

print("\nEjecutando re-entrenamiento supervisado del modelo ML...")
subprocess.run(["python", "training/entrenar_modelo.py"])
