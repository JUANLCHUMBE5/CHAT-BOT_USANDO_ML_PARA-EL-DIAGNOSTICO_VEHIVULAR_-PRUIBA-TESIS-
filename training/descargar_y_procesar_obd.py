import json
import pandas as pd
import requests
import os
import subprocess

# URL oficial del dataset abierto de códigos OBD-II / DTCs en GitHub
URL_OBD_CODES = "https://raw.githubusercontent.com/mytrile/obd-trouble-codes/master/obd-trouble-codes.json"

print("=" * 80)
print("DESCARGADOR AUTOMATICO DE DATASET DE DIAGNOSTICO OBD-II / DTCs")
print("=" * 80)
print(f"Descargando desde: {URL_OBD_CODES}...")

try:
    response = requests.get(URL_OBD_CODES, timeout=10)
    data_json = response.json()
    print(f"-> Descarga exitosa. Total de registros OBD-II recibidos: {len(data_json)}")
except Exception as e:
    print(f"Error al descargar el dataset desde GitHub: {e}")
    exit()

# Mapeador sintáctico al español peruano para traducir códigos clave OBD-II
mapeo_traduccion_obd = {
    "Air Flow": "Filtro de aire suelto o falla de sensor de flujo de aire MAP / MAF",
    "Pressure": "Falla en el sensor de presion del sistema de inyeccion / vacio",
    "Temperature": "Falla en el sensor de temperatura del refrigerante o termostato",
    "Misfire": "Falla de cilindro / bujias desgastadas o bobina de encendido defectuosa",
    "Knock": "Preignicion o cascabeleo en el motor por bujias desgastadas",
    "Oxygen": "Sensor de oxigeno defectuoso (alto consumo de gasolina y humo)",
    "Fuel": "Fuga o fallo en la bomba / inyectores de combustible",
    "Ignition": "Falla en el sistema de encendido o bateria",
    "Brake": "Problema en el sistema de frenos / sensor ABS",
    "Transmission": "Falla en la caja de cambios / fluido de transmision"
}

filas_obd = []

for item in data_json:
    # Extraer el código DTC y su descripción en inglés
    for codigo_dtc, descripcion_en in item.items():
        if codigo_dtc.startswith("P"):  # Códigos del Tren Motriz / Powertrain
            # Mapear al español según palabras clave
            falla_es = "Falla de sensores del sistema del vehiculo"
            for clave_en, traduccion in mapeo_traduccion_obd.items():
                if clave_en.lower() in descripcion_en.lower():
                    falla_es = traduccion
                    break
            
            sintoma_es = f"Luz Check Engine encendida con codigo de falla {codigo_dtc}: {descripcion_en}"
            filas_obd.append({"sintoma": sintoma_es, "falla": falla_es})

df_obd = pd.DataFrame(filas_obd)
# Guardar dataset procesado de OBD-II
ruta_obd_csv = "data/dataset_obd2_descargado.csv"
df_obd.to_csv(ruta_obd_csv, index=False, encoding="utf-8")
print(f"-> Guardado dataset traducido en: {ruta_obd_csv} ({len(df_obd)} filas).")

# Fusionar con el dataset principal del proyecto
ruta_principal = "data/dataset_sintomas.csv"
if os.path.exists(ruta_principal):
    df_base = pd.read_csv(ruta_principal)
    df_final = pd.concat([df_base, df_obd], ignore_index=True)
else:
    df_final = df_obd

df_final.drop_duplicates(subset=['sintoma'], inplace=True)
df_final.to_csv(ruta_principal, index=False, encoding="utf-8")

print("=" * 80)
print(f"¡DATASET DE INTERNET FUSIONADO Y ACTUALIZADO CON EXITO!")
print(f"-> Total acumulado en 'data/dataset_sintomas.csv': {len(df_final)} muestras.")
print("=" * 80)

# Re-entrenar el modelo con la data descargada
print("\nRe-entrenando el modelo de Machine Learning...")
subprocess.run(["python", "training/entrenar_modelo.py"])
