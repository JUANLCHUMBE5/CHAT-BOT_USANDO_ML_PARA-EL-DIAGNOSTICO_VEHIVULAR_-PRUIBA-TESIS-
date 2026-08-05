import pandas as pd
import numpy as np
import random
import os
import subprocess

# Configuración de Semilla
random.seed(42)

# Definimos las categorías principales de fallas y sus combinaciones de lenguaje peruano
fallas_categorias = {
    "Pastillas de freno desgastadas": [
        "siento un chillido agudo al frenar",
        "el carro chilla bastante cuando piso el freno",
        "suena como metal chocando en la llanta cuando freno",
        "se escucha un chirrido feo al frenar en la esquina",
        "el freno chilla feo a baja velocidad"
    ],
    "Fuga de liquido de frenos o aire en el sistema": [
        "el pedal de freno se va hasta el fondo y esta esponjoso",
        "el freno esta muy largo y no frena casi nada",
        "tengo que pisar hasta el fondo el pedal para que pare",
        "siento el pedal de freno blando y el nivel de liquido bajo",
        "el pedal de freno se hunde solo al mantenerlo pisado"
    ],
    "Bujias desgastadas o gasolina de bajo octanaje (preignicion)": [
        "el motor cascabelea fuerte cuando subo una cuesta",
        "siento un cascabeleo en el motor al acelerar fuerte",
        "el carro cascabelea y pierde fuerza en la subida",
        "escucho un sonajero o cascabeleo en el motor al pisar el acelerador",
        "el motor cabecea y cascabelea en tercera marcha"
    ],
    "Bateria descargada o arrancador defectuoso": [
        "el carro no arranca solo hace un click click al girar la llave",
        "no prende el auto no da arranque y las luces estan tenues",
        "giro la llave y no hace nada la bateria esta muerta",
        "el carro no da marcha y el tablero parpadea",
        "no arranca en las mañanas solo suena un tacc seco"
    ],
    "Soportes de motor rotos o inyectores sucios": [
        "el motor tiembla bastante cuando esta parado en el semaforo",
        "el auto vibra mucho en ralenti o cuando esta encendido quieto",
        "siento una vibracion fuerte en el timon y asientos al estar detenido",
        "el motor zapatea al estar neutro",
        "tiembla todo el carro cuando prendo el aire acondicionado parado"
    ],
    "Llantas desalineadas, desbalanceadas o deformadas": [
        "el timon tiembla bastante a mas de 80 kilometros por hora",
        "vibra la direccion del carro cuando voy por la panamericana",
        "el timon zapatea fuerte a alta velocidad",
        "siento que la direccion vibra entre 70 y 90 km/h",
        "el carro se jala para un lado y tiembla el timon"
    ],
    "Amortiguadores reventados o bujes de suspension gastados": [
        "suena un golpe seco en la llanta al pasar un rompemuelles",
        "escucho un trancazo seco en la suspension al pasar por baches",
        "el carro golpea feo abajo al cruzar un bache en carabayllo",
        "suena un golpe fuerte en la rueda delantera derecha al caer en hueco",
        "la suspension suena suelta y golpea al andar"
    ],
    "Juntas homocineticas (palieres) dañadas": [
        "suena un clac clac fuerte al girar todo el timon para doblar",
        "cuando doblo toda la esquina suena un crujido en la llanta",
        "suena clac clac en las ruedas delanteras cuando giro a la izquierda",
        "al dar vuelta en u se escucha un traqueteo en el palier",
        "suena un chasquido continuo cuando doblo el timon"
    ],
    "Filtro de combustible obstruido o inyectores sucios": [
        "el carro se aguanta o pierde fuerza cuando acelero",
        "siento que el auto se chupa y no responde al acelerador",
        "el carro se atranca al querer adelantar un bus",
        "acelero y el carro no avanza se queda aguantado",
        "pierde potencia de la nada cuando acelero en pista"
    ],
    "Sensor de oxigeno defectuoso o bujias en mal estado": [
        "el carro esta consumiendo demasiada gasolina ultimamente",
        "esta tragando combustible como loco y huele raro",
        "el consumo de gasolina se disparo al doble este mes",
        "huele mal el escape y consume mucha gasolina",
        "el tanque de gasolina se rinde muy rapido"
    ],
    "Mezcla rica (demasiado combustible / falla de sensor de oxigeno)": [
        "esta botando humo negro espeso por el tubo de escape",
        "sale humo negro y mancha de hollin el suelo al acelerar",
        "bota humo oscuro y carbon por el escape",
        "sale humo negro con olor a gasolina mal quemada",
        "al acelerar a fondo bota una nube de humo negro"
    ],
    "El motor esta consumiendo aceite (anillos de piston gastados)": [
        "sale humo azul con olor a aceite quemado por el escape",
        "bota humo azuloso continuo cuando acelero",
        "el motor consume aceite y bota humo azul por el tubo",
        "bota humo garzo azulado al salir en primera",
        "tengo que rellenar aceite cada semana y bota humo azul"
    ],
    "Soplo de empaque de culata (ingreso de refrigerante al motor)": [
        "sale bastante humo blanco espeso por el tubo de escape",
        "bota humo blanco como vapor y se consume el agua del radiador",
        "el motor calienta y bota humo blanco espeso constante",
        "se mezcla el agua con el aceite y bota humo blanco",
        "bota bastante vapor y agua por el tubo de escape"
    ],
    "Alternador defectuoso o faja suelta": [
        "suena un chillido agudo de faja debajo del capo",
        "el motor chilla feo al encenderlo en las mañanas",
        "suena un silbido agudo continuo en la faja del alternador",
        "prende la luz de la bateria en el tablero y chilla la faja",
        "chilla la faja al prender las luces altas o aire"
    ],
    "Valvula IAC sucia u obstruida (control de minimo)": [
        "el motor se apaga solo cuando bajo la velocidad o freno",
        "al llegar a una esquina o semaforo el carro se apaga de la nada",
        "se apaga el motor al poner neutro o soltar el acelerador",
        "el minimo esta inestable y el carro se apaga solo",
        "se apaga en cada rompemuelles si no lo mantengo acelerado"
    ]
}

# Modificadores de contexto peruano para multiplicar los ejemplos (Augmentation)
prefijos = ["hola maestro", "buenas tardes maestro", "tengo un problema", "amigo una consulta", "mi carro presenta", "sabes que", "resulta que"]
sufijos = ["en carabayllo", "ultimamente", "desde ayer", "cuando salgo a trabajar", "en la pista", "al andar"]

dataset_filas = []

# Generar combinaciones sintéticas
for falla, frases_base in fallas_categorias.items():
    for frase in frases_base:
        # Agregar la frase base limpia
        dataset_filas.append({"sintoma": frase, "falla": falla})
        
        # Generar variaciones con prefijos y sufijos
        for _ in range(3):
            p = random.choice(prefijos)
            s = random.choice(sufijos)
            frase_combinada = f"{p} {frase} {s}".strip()
            dataset_filas.append({"sintoma": frase_combinada, "falla": falla})

df_ampliado = pd.DataFrame(dataset_filas)
# Eliminar duplicados si los hubiera
df_ampliado.drop_duplicates(subset=['sintoma'], inplace=True)

# Guardar en data/dataset_sintomas.csv
output_path = "data/dataset_sintomas.csv"
df_ampliado.to_csv(output_path, index=False, encoding="utf-8")

print("=" * 80)
print(f"¡DATASET AMPLIADO CON ÉXITO!")
print(f"-> Total de muestras generadas: {len(df_ampliado)} filas.")
print(f"-> Categorías de falla cubiertas: {len(fallas_categorias)} tipos de averías.")
print(f"-> Guardado en: {output_path}")
print("=" * 80)

# Ejecutar el entrenamiento automáticamente
print("\nIniciando re-entrenamiento del modelo de Machine Learning...")
subprocess.run(["python", "training/entrenar_modelo.py"])
