import pandas as pd
import random
import os
import subprocess

random.seed(2026)

print("=" * 80)
print("MEGA EXPANSIÓN INTERNACIONAL DE DATASET (BRASIL, LATAM, USA & ALEMANIA)")
print("=" * 80)

# Categorías específicas de vehículos de mercado Latinoamericano (Brasil/LATAM) y Europeo (Alemania)
fallas_internacionales = {
    # BRASIL & LATAM (Fiat Fire/Firefly, Chevrolet Spec/Ecotec, Renault K4M/HR16, VW EA111/EA211)
    "Falla en sistema Flex / Bi-combustible (Alcohol/Etanol en autos brasilenosis)": [
        "carro brasilero falla en frio al cambiar de gasolina a etanol alcohol",
        "sensor de AF (Air Fuel Ratio) no reconoce mezcla de etanol",
        "bico injetor sujo em motor flex"
    ],
    "Falla en caja robotizada Dualogic / I-Motion / Easytronic (Fiat / VW LATAM)": [
        "caja dualogic parpadea en N y se desengancha sola en semaforo",
        "bomba de presion del robot i-motion suena sin parar",
        "falta de presion hidraulica en robotizador de caja automatizada"
    ],
    "Falla de correa dentada bañada en aceite (Motor Ford 1.0 3-Cilindros Dragon / GM Turbo)": [
        "correa de distribucion desprendio caucho y tupio coladera de bomba de aceite",
        "baja presion de aceite por restos de faja bañada en aceite",
        "ruido de taques en motor 3 cilindros turbo"
    ],

    # ALEMANIA & EUROPA (Volkswagen / Audi TSI-TFSI, BMW Valvetronic, Mercedes BlueTEC, Porsche PDK)
    "Falla en actuador de turbocompresor o VGT en motores alemanes TSI / TFSI": [
        "perdió potencia brusca el motor TSI y prendió testigo EPC",
        "wastegate de turbo con juego y DTC P0299 bajo presion de sobrealimentacion",
        "actuador electronico de turbo trabado"
    ],
    "Falla de descarbonizacion e inyeccion directa GDI (Acumulacion de carbon en valvulas)": [
        "motor inyeccion directa GDI tiembla en minimo y cabecea en frio",
        "acumulacion severa de carbonilla en valvulas de admision GDI",
        "codigo de misfire P0300 en motor inyeccion directa"
    ],
    "Falla en sistema de sincronizacion variable de valvulas (VVT / VVT-i / Valvetronic)": [
        "solenoide de actuador de levas ruidoso al encender en frio",
        "ruido de matraca al dar arranque en el piñon VVT",
        "codigo DTC P0011 / P0014 avance de levas fuera de rango"
    ],
    "Falla en filtro de particulas DPF / FAP y sistema AdBlue DEF (Diésel Euro 5/6)": [
        "mensaje de regeneracion DPF saturado en tablero de camioneta diesel",
        "nivel de adblue no sube y contador de arranque bloqueado",
        "humo denso y bloqueo de potencia por filtro de particulas tapado"
    ],

    # ESTADOS UNIDOS & ASIÁTICOS (Ford EcoBoost, Chevrolet Vortec/Ecotec, Dodge Hemi, Honda VTEC, Toyota Hybrid)
    "Falla en modulo de bomba de gasolina FSCM / PEM (Ford / Chevrolet USA)": [
        "carro se apaga andando por sobrecalentamiento de modulo de bomba",
        "bomba de gasolina inoperativa por conector quemado en FSCM",
        "codigo P0627 circuito de control de bomba de combustible"
    ],
    "Falla de cuerpo de aceleracion electronico TAC (Drive-by-Wire)": [
        "pedal de acelerador no responde y tablero marca potencia de motor reducida",
        "sensor TPS de pedal descalibrado",
        "cuerpo de aceleracion se queda trabado en modo limp home"
    ]
}

modismos_regionales = [
    "maestro una consulta", "tengo una falla en mi carro", "el mecanico de carabayllo dice que",
    "hola buenas tardes", "mi auto brasilero presenta", "en la escaner salio",
    "maestro mi caña", "amigo en subida"
]

filas_exp = []
for falla, frases in fallas_internacionales.items():
    for f in frases:
        filas_exp.append({"sintoma": f, "falla": falla})
        for _ in range(120):  # Augmentación x120
            m = random.choice(modismos_regionales)
            filas_exp.append({"sintoma": f"{m} {f}".strip(), "falla": falla})

df_exp = pd.DataFrame(filas_exp)

path_csv = "data/dataset_sintomas.csv"
if os.path.exists(path_csv):
    df_ant = pd.read_csv(path_csv)
    df_tot = pd.concat([df_ant, df_exp], ignore_index=True)
else:
    df_tot = df_exp

df_tot.drop_duplicates(subset=['sintoma'], inplace=True)
df_tot.to_csv(path_csv, index=False, encoding="utf-8")

print(f"-> Dataset final masivo expandido a {len(df_tot)} muestras totales!")

print("\nRe-entrenando el modelo de Machine Learning con el Super Dataset Internacional...")
subprocess.run(["python", "training/entrenar_modelo.py"])
