import pandas as pd
import random
import os
import subprocess

random.seed(2026)

print("=" * 80)
print("AMPLIANDO DATASET A TODAS LAS PARTES Y SISTEMAS DEL AUTO (30,000+ MUESTRAS)")
print("=" * 80)

# Matriz exhaustiva de fallas por cada sistema del auto
sistemas_auto = {
    # 1. MOTOR Y SISTEMA DE DISTRIBUCIÓN
    "Empaque de culata soplado": [
        "bota vapor blanco por el escape y junta agua con aceite",
        "el radiador bota burbujas con el motor encendido",
        "aceite de motor parece leche con cafe chocolatada"
    ],
    "Faja de distribucion / tiempo destensada o rota": [
        "motor hizo un ruido seco feo y se apago al instante no vuelve a arrancar",
        "ruido de latigazo en la tapa de distribucion",
        "arbol de levas no gira al dar arranque"
    ],
    "Bomba de aceite defectuosa o baja presion de lubricacion": [
        "testigo de la aceitera se prende en rojo en el tablero",
        "ruido de buzos y taques sonando como maquina de coser",
        "presion de aceite cae a cero en caliente"
    ],

    # 2. SISTEMA DE TRANSMISIÓN (MECÁNICA Y AUTOMÁTICA CVT/DSG)
    "Disco de embrague (clutch) gastado o patinando": [
        "el motor acelera y ruge pero el carro no agarra velocidad en subida",
        "embrague resbala al pasar cambios",
        "olor a quemado feo al soltar el pedal de embrague"
    ],
    "Caja automatica CVT o DSG con sobrecalentamiento / solenoide trancado": [
        "caja automatica da tirones y golpes al pasar de P a D",
        "cambios automaticos no entran o se queda trabado en segunda",
        "luz de alerta de transmision automatica encendida"
    ],
    "Rodajes de caja mecanica o diferencial gastados": [
        "zumbido fuerte en la caja de cambios que aumenta con la velocidad",
        "suena como avion al andar a mas de 60 km/h en quinta",
        "caja de cambios vibra e palanca tiembla"
    ],

    # 3. SISTEMA DE FRENOS Y ABS
    "Pastillas o zapatas de freno totalmente desgastadas": [
        "chillido de fierro con fierro al pisar el freno en la rueda",
        "ruido metalico agudo al detenerse",
        "freno no agarra bien y chirria seco"
    ],
    "Discos de freno rectificados en exceso o alabeados": [
        "pedal de freno y timon tiemblan bastante al frenar bajando pendiente",
        "vibracion fuerte en la pierna al pisar el freno",
        "freno zapatea feo"
    ],
    "Sensor de velocidad ABS de rueda sucio o dañado": [
        "testigo de ABS y freno de mano encendidos juntos en el tablero",
        "freno patea brusco al detenerse despacio",
        "codigo DTC C0035 de sensor de rueda"
    ],

    # 4. DIRECCIÓN Y SUSPENSIÓN
    "Cremallera de direccion asistida (EPS o Hidraulica) con juego o fuga": [
        "timon duro como piedra para doblar en esquinas",
        "golpeteo en el volante al andar en pista afirmada",
        "fuga de fluido de direccion en el guardapolvo"
    ],
    "Amortiguadores reventados o bujes de muelles gastados": [
        "llanta rebota como pelota al pasar rompemuelles",
        "carro se hamaca feo en curvas",
        "golpe seco al caer en baches"
    ],
    "Junta homocinetica / palier con tripoide destruido": [
        "suena traca traca traca muy fuerte al dar vuelta en U",
        "crujido feo en la rueda delantera al acelerar doblando",
        "grasa de palier botada por el guardapolvo roto"
    ],

    # 5. SISTEMA ELÉCTRICO Y CLIMATIZACIÓN (A/C)
    "Alternador defectuoso o placa de diodos quemada": [
        "testigo de bateria prendido y las luces se bajan en la noche",
        "bateria nueva se descarga sola en dos dias",
        "voltimetro marca menos de 12 voltios andando"
    ],
    "Compresor de aire acondicionado (A/C) trabado o fuga de gas R134a": [
        "aire acondicionado bota aire caliente y no me enfria nada",
        "suena chillido feo al prender el botón A/C",
        "compresor de aire no engancha el embrague magnetico"
    ],
    "Motor de arrancador / solenoide pegado": [
        "al girar la llave solo suena un clack seco y no da marcha",
        "arrancador arrastra lento como sin fuerza",
        "solenoide no empuja el bendix"
    ],

    # 6. CARROCERÍA, CHAPAS Y CONFORT
    "Mecanismo de chapa / cerradura de puerta desalineada o trabada": [
        "la chapa de la puerta esta inclinada y no encaja en el marco",
        "la puerta no abre por dentro ni por fuera",
        "pestillo electrico salta y no traba la chapa"
    ],
    "Elevador de vidrio / alzacristales quemado o guaya rota": [
        "vidrio de la ventana cayo al fondo del tapizado de la puerta",
        "motor del elevalunas suena pero la luna no sube",
        "vidrio sube chueco y se traba"
    ],

    # 7. CAMIONES Y VEHÍCULOS PESADOS DIÉSEL
    "Válvula de freno de aire o secador APS obstruido (Camiones)": [
        "presion de aire en los tanques del camion no llega a 8 bares",
        "freno de pedal de camión duro y fuga constante por la purga",
        "camion bloqueado en los muelles de parqueo"
    ],
    "Turbocompresor picado o fuga en el Intercooler (Diésel)": [
        "camion pierde torque en subidas pesadas y bota humo negro",
        "silbido de fuga de aire en mangueras de turbo",
        "geometria variable del turbo pegada"
    ],

    # 8. VEHÍCULOS ELÉCTRICOS E HÍBRIDOS (EV/HEV)
    "Bateria de alto voltaje (HV) con celda sulfatada (Prius / EV)": [
        "ventilador de la bateria de alto voltaje suena fuerte todo el tiempo",
        "luz de triangulo rojo de averia del sistema hibrido",
        "bateria HV se descarga en 2 minutos de uso"
    ],
    "Inversor IGBT o bomba de agua de inversor inoperativa": [
        "vehiculo electrico marca Check EV y no entra en modo Ready",
        "sobrecalentamiento en modulo inversor de corriente",
        "codigo DTC P0A1B de inversor electrico"
    ]
}

modismos_peruanos = [
    "buenas tardes maestro", "tengo una falla en mi carro", "en el taller me dijeron que",
    "amigo una consulta", "mi auto presenta", "al andar por carabayllo", "resulta que",
    "maestro mi caña", "en la panamericana norte"
]

filas_nuevas = []
for falla, frases in sistemas_auto.items():
    for f in frases:
        filas_nuevas.append({"sintoma": f, "falla": falla})
        for _ in range(80):  # Augmentación x80 por síntoma
            m = random.choice(modismos_peruanos)
            filas_nuevas.append({"sintoma": f"{m} {f}".strip(), "falla": falla})

df_nuevas = pd.DataFrame(filas_nuevas)

path_csv = "data/dataset_sintomas.csv"
if os.path.exists(path_csv):
    df_ant = pd.read_csv(path_csv)
    df_tot = pd.concat([df_ant, df_nuevas], ignore_index=True)
else:
    df_tot = df_nuevas

df_tot.drop_duplicates(subset=['sintoma'], inplace=True)
df_tot.to_csv(path_csv, index=False, encoding="utf-8")

print(f"-> Dataset final expandido a {len(df_tot)} filas!")

print("\nRe-entrenando el modelo supervisado con la cobertura de todas las partes...")
subprocess.run(["python", "training/entrenar_modelo.py"])
