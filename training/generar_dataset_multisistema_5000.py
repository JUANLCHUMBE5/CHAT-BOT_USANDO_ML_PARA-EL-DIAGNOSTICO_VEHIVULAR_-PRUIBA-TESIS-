import pandas as pd
import numpy as np
import random
import os
import subprocess

# Semilla de aleatoriedad
random.seed(101)

# DEFINICIÓN MULTISISTEMA COMPLETO DE VEHÍCULOS (50+ CATEGORÍAS EN 10 SUBSISTEMAS)
subsistemas_automotrices = {
    # 1. SISTEMA DE FRENOS
    "Pastillas de freno desgastadas": [
        "chillido feo al frenar", "ruido de metal con metal en las ruedas al pisar el freno", "chilla la rueda delantera cuando freno", "chirrido agudo en el pedal de freno"
    ],
    "Fuga de liquido de frenos o aire en cañerias": [
        "pedal de freno esponjoso y se hunde hasta el fondo", "freno muy largo y no frena casi nada", "el nivel de liquido de frenos baja solo", "tengo que bombear el freno para que agarre"
    ],
    "Fallo en el servo freno (booster)": [
        "pedal de freno duro como una piedra y no frena", "tengo que hacer mucha fuerza con la pierna para frenar", "el freno esta hiper duro"
    ],
    "Discos de freno deformados o alabeados": [
        "el timon y el pedal de freno vibran bastante al frenar a alta velocidad", "tiembla el pedal cuando piso el freno despacio"
    ],

    # 2. SUSPENSIÓN Y DIRECCIÓN
    "Amortiguadores reventados o bujes de suspension gastados": [
        "golpe seco o trancazo en la llanta al pasar por rompemuelles", "ruido de cazoleta en huecos", "la suspension golpea feo abajo", "el carro se hamaca demasiado al frenar"
    ],
    "Juntas homocineticas (palieres) dañadas": [
        "suena clac clac fuerte al girar todo el timon para doblar", "crujido en la llanta al dar vuelta en U", "traqueteo en el palier delantero al doblar la esquina"
    ],
    "Llantas desalineadas, desbalanceadas o deformadas": [
        "el timon tiembla bastante a mas de 80 km/h", "direccion vibra en la autopista", "el carro se jala solo hacia un lado en pista recta"
    ],
    "Caja o cremallera de direccion asistida con fuga": [
        "timon duro para girar y suena un zumbido al doblar", "fuga de aceite de direccion en el suelo", "la direccion hidraulica esta durisima"
    ],

    # 3. EMBRAGUE Y TRANSMISIÓN
    "Disco de embrague (clutch) desgastado o patinando": [
        "el motor revoluciona alto pero el carro no avanza con fuerza", "el carro se queda sin fuerza en subidas y huele a quemado", "el embrague patina al cambiar de marcha"
    ],
    "Bombin o cable de embrague desajustado": [
        "los cambios rascados o duros de entrar", "el pedal de embrague no regresa bien", "cuesta meter primera y retroceso"
    ],
    "Falta o degradacion de aceite de caja de cambios": [
        "zumbido constante en la caja de cambios al andar", "suena un canto feo en la caja en neutro", "los cambios botan la marcha solos"
    ],

    # 4. CARROCERÍA, CERRADURAS Y ACCESORIOS
    "Daño o desalineacion en la chapa / mecanismo de seguro de la puerta": [
        "la chapa de la puerta esta inclinada o trabada y no abre", "al aplastar el control la puerta sigue bloqueada", "el pestillo de la puerta se quedo chueco", "la cerradura no encaja ni abre"
    ],
    "Elevalunas / levanta vidrios electrico defectuoso": [
        "la ventana del carro no sube ni baja", "se escucho un chasquido y el vidrio cayo al fondo de la puerta", "el motor del elevador de ventana no responde"
    ],
    "Limpiaparabrisas / motor pluma quemado": [
        "las plumas del limpiaparabrisas no se mueven", "el agua del limpiaparabrisas no sale", "las plumas se quedaron trabadas a la mitad"
    ],

    # 5. SISTEMA ELÉCTRICO Y ENCENDIDO
    "Bateria descargada o arrancador defectuoso": [
        "el carro no arranca solo hace un click seco", "tablero tenue y no da marcha", "bateria totalmente muerta", "el arrancador gira pesado"
    ],
    "Alternador defectuoso o faja suelta": [
        "luz de bateria prendida en el tablero", "faja del alternador chilla feo al encender", "las luces del carro van bajando de intensidad al andar"
    ],
    "Falla en el rele o motor del ventilador del radiador": [
        "el electroventilador no prende y el agua hierve", "el ventilador se queda prendido directo y agota la bateria"
    ],

    # 6. INYECCIÓN Y COMBUSTIBLE
    "Bujias desgastadas o bobina de encendido defectuosa": [
        "motor cascabelea en subidas", "el carro tiembla y se chupa al acelerar", "falla de cilindro y perdida de potencia"
    ],
    "Filtro de combustible o inyectores sucios": [
        "el carro se agunta al acelerar fuerte", "se atranca al acelerar", "falta de pique y respuesta floja"
    ],
    "Bomba de gasolina / combustible quemada o sin presion": [
        "el carro da arranque pero no llega a encender", "la bomba de gasolina no suena al girar la llave", "se apaga el carro en marcha por falta de gasolina"
    ],
    "Sensor de oxigeno defectuoso": [
        "alto consumo de gasolina y bota humo negro", "el carro traga demasiado combustible", "luz de check engine por mezcla rica"
    ],

    # 7. REFRIGERACIÓN Y MOTOR
    "Soplo de empaque de culata": [
        "sale humo blanco espeso por el tubo de escape", "se mezcla el agua con el aceite", "el radiador bota burbujas y consume agua"
    ],
    "Consumo de aceite por anillos de piston gastados": [
        "bota humo azul con olor a aceite quemado", "tengo que echarle un litro de aceite cada semana", "bota humo azul al acelerar"
    ],
    "Fuga en mangueras de refrigerante o radiador picado": [
        "el motor calienta rapido y charco de agua abajo", "el nivel de refrigerante baja sin razon aparente"
    ],
    "Valvula IAC sucia u obstruida (minimo)": [
        "el carro se apaga solo al soltar el acelerador o en semaforos", "el minimo oscila sube y baja solo"
    ]
}

# Modificadores de contexto del conductor en Carabayllo
prefijos = [
    "maestro una consulta", "buenas tardes mecanico", "tengo un problema con mi auto", "sabes que", "resulta que en mi carro", 
    "amigo mi auto presenta", "hace dos dias noto que", "al salir a trabajar", "siento que"
]

sufijos = [
    "en carabayllo", "cuando voy manejando", "al acelerar", "en las mañanas", "en la pista", "al pasar un rompemuelles", "de la nada"
]

registros = []

# Generación masiva por permutación sintáctica
for falla, frases in subsistemas_automotrices.items():
    for frase in frases:
        # Frase limpia
        registros.append({"sintoma": frase, "falla": falla})
        
        # Variaciones con contexto real
        for _ in range(8):
            p = random.choice(prefijos)
            s = random.choice(sufijos)
            registros.append({"sintoma": f"{p} {frase} {s}".strip(), "falla": falla})

df_multisistema = pd.DataFrame(registros)
df_multisistema.drop_duplicates(subset=['sintoma'], inplace=True)

# Unir con dataset principal
ruta_principal = "data/dataset_sintomas.csv"
if os.path.exists(ruta_principal):
    df_base = pd.read_csv(ruta_principal)
    df_completo = pd.concat([df_base, df_multisistema], ignore_index=True)
else:
    df_completo = df_multisistema

df_completo.drop_duplicates(subset=['sintoma'], inplace=True)
df_completo.to_csv(ruta_principal, index=False, encoding="utf-8")

print("=" * 80)
print(f"¡DATASET MULTISISTEMA DE AUTOS GENERADO EXITOSAMENTE!")
print(f"-> Total de muestras acumuladas: {len(df_completo)} filas.")
print(f"-> Cobertura: {len(subsistemas_automotrices)} categorías principales de averías automotrices.")
print("=" * 80)

# Re-entrenar modelo
print("\nRe-entrenando el modelo supervisado con la base multisistema...")
subprocess.run(["python", "training/entrenar_modelo.py"])
