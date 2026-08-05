import json
import pandas as pd
import requests
import os
import random
import subprocess

random.seed(42)

print("=" * 80)
print("DESCARGADOR Y CONSOLIDADOR EXPANDIDO DE DATASETS DE INTERNET")
print("=" * 80)

# URL 1: DTC Codes (mytrile/obd-trouble-codes)
URL_OBD = "https://raw.githubusercontent.com/mytrile/obd-trouble-codes/master/obd-trouble-codes.json"
# URL 2: Generic DTC DB (todrobbins/dtcdb)
URL_DTC_GENERIC = "https://raw.githubusercontent.com/todrobbins/dtcdb/master/dtcs/generic.csv"

nuevas_filas = []

# 1. Descargar OBD Trouble Codes
print(f"1. Obteniendo dataset de GitHub (OBD Codes): {URL_OBD}...")
try:
    resp = requests.get(URL_OBD, timeout=10)
    data_json = resp.json()
    print(f"   -> OBD JSON recibido: {len(data_json)} registros.")
    
    mapeo_obd = {
        "Air Flow": "Filtro de aire suelto o falla de sensor MAP / MAF",
        "Pressure": "Falla en el sensor de presion del sistema de inyeccion / vacio",
        "Temperature": "Falla en el sensor de temperatura del refrigerante o termostato",
        "Misfire": "Falla de cilindro / bujias desgastadas o bobina de encendido",
        "Knock": "Preignicion o cascabeleo en el motor por bujias desgastadas",
        "Oxygen": "Sensor de oxigeno defectuoso (alto consumo de gasolina)",
        "Fuel": "Fuga o fallo en la bomba / inyectores de combustible",
        "Ignition": "Falla en el sistema de encendido o bateria",
        "Brake": "Problema en el sistema de frenos / sensor ABS",
        "Transmission": "Falla en la caja de cambios / fluido de transmision",
        "Camshaft": "Desfasamiento en el sensor de posicion del arbol de levas",
        "Crankshaft": "Falla en el sensor de posicion del ciguenal",
        "Throttle": "Cuerpo de aceleracion suelto o descalibrado",
        "EGR": "Valvula EGR atascada por hollin"
    }

    for item in data_json:
        for codigo, desc in item.items():
            if codigo.startswith("P") or codigo.startswith("C") or codigo.startswith("B"):
                falla = "Falla de sensores del sistema del vehiculo"
                for clave, trad in mapeo_obd.items():
                    if clave.lower() in desc.lower():
                        falla = trad
                        break
                sintoma = f"Codigo de falla {codigo} detectado en escaner: {desc}"
                nuevas_filas.append({"sintoma": sintoma, "falla": falla})
except Exception as e:
    print(f"   -> Advertencia al descargar OBD JSON: {e}")

# 2. Descargar Generic DTC DB (CSV)
print(f"\n2. Obteniendo dataset de GitHub (DTC Generic DB): {URL_DTC_GENERIC}...")
try:
    resp_csv = requests.get(URL_DTC_GENERIC, timeout=10)
    if resp_csv.status_code == 200:
        lines = resp_csv.text.splitlines()
        print(f"   -> DTC CSV recibido: {len(lines)} lineas.")
        for line in lines[1:500]:  # Procesar primeras 500 líneas
            parts = line.split(',')
            if len(parts) >= 2:
                code = parts[0].strip().replace('"', '')
                desc = parts[1].strip().replace('"', '')
                if code.startswith("P"):
                    nuevas_filas.append({
                        "sintoma": f"Escaner OBD indica codigo {code}: {desc}",
                        "falla": "Falla de sensores o control de motor"
                    })
except Exception as e:
    print(f"   -> Advertencia al descargar DTC CSV: {e}")

df_descargado = pd.DataFrame(nuevas_filas)
print(f"\nTotal de muestras extraídas de la web: {len(df_descargado)} filas.")

# 3. Fusionar con data/dataset_sintomas.csv
ruta_principal = "data/dataset_sintomas.csv"
if os.path.exists(ruta_principal):
    df_base = pd.read_csv(ruta_principal)
    df_final = pd.concat([df_base, df_descargado], ignore_index=True)
else:
    df_final = df_descargado

df_final.drop_duplicates(subset=['sintoma'], inplace=True)
df_final.to_csv(ruta_principal, index=False, encoding="utf-8")

print("=" * 80)
print(f"¡DATASETS INTEGRADOS EXITOSAMENTE AL PROYECTO!")
print(f"-> Archivo actualizado: {ruta_principal}")
print(f"-> Total acumulado: {len(df_final)} muestras.")
print("=" * 80)

# Re-entrenar modelo automáticamente
print("\nRe-entrenando el modelo de Machine Learning con el nuevo dataset ampliado...")
subprocess.run(["python", "training/entrenar_modelo.py"])
