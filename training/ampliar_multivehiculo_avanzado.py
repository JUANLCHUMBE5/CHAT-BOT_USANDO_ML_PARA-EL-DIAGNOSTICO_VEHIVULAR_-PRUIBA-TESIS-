import pandas as pd
import numpy as np
import random
import os
import subprocess

random.seed(2026)

# DATASET EXPANDIDO MULTIVEHÍCULO: AUTOS, CAMIONES Y VEHÍCULOS ELÉCTRICOS (EV/HEV)
fallas_multivehiculo = {
    # === 1. CAMIONES Y VEHÍCULOS PESADOS (DIÉSEL / TRANSPORTE) ===
    "Fugas de aire o fallos en el sistema de frenos neumático (Camiones)": [
        "escucho un soplido continuo de aire en los tanques del camion", "el pedal de freno de aire esta duro y la presion de aire no sube en los relojes",
        "los frenos de aire del camion se quedan clavados", "fuga de aire en la valvula de purga del camion"
    ],
    "Falla en el turbocompresor o intercooler (Camiones Diésel)": [
        "el camion bota humo negro denso y no tiene fuerza para jalar carga", "zumbido fuerte en el turbo al acelerar el camion",
        "fuga de aceite en las mangueras del intercooler del camion", "el camion pierde presion de sobrealimentacion en subidas"
    ],
    "Fuga o baja presion en sistema Common Rail Diésel (Camiones/Pickups)": [
        "el camion demora bastante en arrancar en frio", "cascabelea el motor diesel bajo carga pesada",
        "inyectores diesel goteando y bota humo blanco con olor a petroleo", "fuga en el riel de alta presion de petroleo"
    ],

    # === 2. VEHÍCULOS ELÉCTRICOS E HÍBRIDOS (EV / HEV) ===
    "Degradacion o falla en paquete de bateria de alto voltaje (EV / Híbridos)": [
        "la autonomia de la bateria del auto electrico cae bruscamente", "luz de advertencia de sistema hibrido en el tablero",
        "el auto electrico no acepta la carga rapida", "el indicador de bateria del auto hibrido pasa de lleno a vacio rapido"
    ],
    "Fallo en inversor de corriente o motor electrico (EV)": [
        "el auto electrico no pasa a modo ready y no avanza", "zumbido agudo inusual en el motor electrico al acelerar",
        "falla de aislamiento de alto voltaje en el inversor", "el vehiculo hibrido no conmuta al motor de gasolina"
    ],
    "Falla en sistema de frenado regenerativo (EV / Híbridos)": [
        "el freno regenerativo no retiene el auto al soltar el acelerador", "sensacion brusca o jalón al frenar en el auto hibrido",
        "luz de advertencia de frenos regenerativos encendida"
    ],
    "Foco o falla en sistema de refrigeracion de bateria/inversor (EV)": [
        "mensaje de sobrecalentamiento de la bateria de alto voltaje", "bomba de agua del inversor no circula refrigerante especial",
        "el auto electrico limita la potencia por alta temperatura en la bateria"
    ]
}

# Modificadores de vehículos pesados y eléctricos
prefijos_esp = ["maestro una consulta", "tengo un camion", "mi auto electrico", "en mi auto hibrido", "tengo un vehiculo pesado", "resulta que mi pickup diesel"]
sufijos_esp = ["en carretera", "con carga pesada", "al cargar la bateria", "en ruta larga", "al acelerar", "en carabayllo"]

registros_nuevos = []

for falla, frases in fallas_multivehiculo.items():
    for frase in frases:
        registros_nuevos.append({"sintoma": frase, "falla": falla})
        for _ in range(6):
            p = random.choice(prefijos_esp)
            s = random.choice(sufijos_esp)
            registros_nuevos.append({"sintoma": f"{p} {frase} {s}".strip(), "falla": falla})

df_multivehiculo = pd.DataFrame(registros_nuevos)
df_multivehiculo.drop_duplicates(subset=['sintoma'], inplace=True)

# Unir con el dataset principal
ruta_principal = "data/dataset_sintomas.csv"
if os.path.exists(ruta_principal):
    df_base = pd.read_csv(ruta_principal)
    df_final = pd.concat([df_base, df_multivehiculo], ignore_index=True)
else:
    df_final = df_multivehiculo

df_final.drop_duplicates(subset=['sintoma'], inplace=True)
df_final.to_csv(ruta_principal, index=False, encoding="utf-8")

print("=" * 80)
print("¡CATEGORÍAS DE CAMIONES Y VEHÍCULOS ELÉCTRICOS INTEGRADAS!")
print(f"-> Total acumulado en 'data/dataset_sintomas.csv': {len(df_final)} muestras.")
print("=" * 80)

# Re-entrenar modelo
print("\nRe-entrenando el modelo de Machine Learning multivehículo...")
subprocess.run(["python", "training/entrenar_modelo.py"])
