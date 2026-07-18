import pandas as pd

# Definimos una lista de datos inicial con síntomas en español (adaptados al contexto de talleres mecánicos)
# asociados a su respectivo diagnóstico (falla).
datos = [
    # Sistema de Frenos
    {"sintoma": "siento un chillido feo al frenar el carro", "falla": "Pastillas de freno desgastadas"},
    {"sintoma": "el carro chilla cuando piso el freno", "falla": "Pastillas de freno desgastadas"},
    {"sintoma": "suena como metal chocando cuando freno", "falla": "Pastillas de freno desgastadas / discos dañados"},
    {"sintoma": "el pedal de freno se va hasta el fondo y se siente esponjoso", "falla": "Fuga de liquido de frenos o aire en el sistema"},
    {"sintoma": "el freno esta muy largo y no frena bien", "falla": "Fuga de liquido de frenos o aire en el sistema"},
    {"sintoma": "tengo que pisar muy fuerte el freno para que pare", "falla": "Problema en el servo freno (booster) o pastillas cristalizadas"},
    {"sintoma": "el pedal de freno esta duro y no frena casi nada", "falla": "Fallo en el servo freno (booster)"},
    {"sintoma": "el carro se jala para un lado cuando freno", "falla": "Calaper de freno atascado o desgaste desigual"},

    # Sistema de Motor / Encendido
    {"sintoma": "el motor cascabelea cuando subo una cuesta o acelero fuerte", "falla": "Bujias desgastadas o gasolina de bajo octanaje (preignicion)"},
    {"sintoma": "siento un cascabeleo en el motor al acelerar", "falla": "Bujias desgastadas o gasolina de bajo octanaje (preignicion)"},
    {"sintoma": "el carro no arranca solo hace un click click al girar la llave", "falla": "Bateria descargada o arrancador defectuoso"},
    {"sintoma": "no prende el auto no da arranque y las luces estan bajas", "falla": "Bateria dañada o descargada"},
    {"sintoma": "el carro demora en arrancar en las mañanas cuando esta frio", "falla": "Bujias desgastadas o bobinas con falla de corriente"},
    {"sintoma": "el motor tiembla mucho cuando esta parado en el semaforo", "falla": "Soportes de motor rotos o falla de cilindro (misfire)"},
    {"sintoma": "el auto tiembla en ralenti o cuando esta encendido pero quieto", "falla": "Soportes de motor rotos o inyectores sucios"},
    {"sintoma": "el motor se apaga de la nada cuando bajo la velocidad", "falla": "Valvula IAC sucia u obstruida (control de minimo)"},

    # Sistema de Suspencion y Direccion
    {"sintoma": "el timon tiembla bastante cuando voy a mas de 80 kilometros por hora", "falla": "Llantas desalineadas, desbalanceadas o deformadas"},
    {"sintoma": "vibra la direccion del carro a alta velocidad", "falla": "Llantas desalineadas, desbalanceadas o deformadas"},
    {"sintoma": "suena un golpe seco en la llanta cuando paso por un bache o rompemuelles", "falla": "Amortiguadores reventados o bujes de suspension gastados"},
    {"sintoma": "suena un clac clac fuerte al girar todo el timon para doblar", "falla": "Juntas homocineticas (palieres) dañadas"},
    {"sintoma": "cuando doblo la esquina suena un crujido en la direccion", "falla": "Juntas homocineticas o terminales de direccion desgastados"},
    {"sintoma": "el carro se va hacia la derecha si suelto el timon", "falla": "Falta de alineacion y balanceo en el eje delantero"},

    # Sistema de Combustible / Inyeccion
    {"sintoma": "el carro se aguanta o pierde fuerza cuando acelero", "falla": "Filtro de combustible obstruido o inyectores sucios"},
    {"sintoma": "siento que el auto pierde potencia y no responde al acelerador", "falla": "Filtro de combustible obstruido o inyectores sucios"},
    {"sintoma": "el carro esta consumiendo demasiada gasolina ultimamente", "falla": "Sensor de oxigeno defectuoso o bujias en mal estado"},
    {"sintoma": "huele mucho a gasolina dentro del carro y bota humo", "falla": "Fuga en la linea de combustible o inyectores goteando"},

    # Escape y Gases
    {"sintoma": "esta botando humo negro por el tubo de escape", "falla": "Mezcla rica (demasiado combustible / falla de sensor de oxigeno)"},
    {"sintoma": "sale humo azul con olor a aceite quemado por el escape", "falla": "El motor esta consumiendo aceite (anillos de piston o retenes de valvula gastados)"},
    {"sintoma": "sale bastante humo blanco espeso por el tubo de escape", "falla": "Soplo de empaque de culata (ingreso de refrigerante al motor)"},
    {"sintoma": "el tubo de escape suena muy fuerte como si estuviera roto", "falla": "Tubo de escape roto o silenciador dañado"}
]

# Crear un DataFrame de Pandas
df = pd.DataFrame(datos)

# Guardar a un archivo CSV en la carpeta data
import os
os.makedirs("data", exist_ok=True)
df.to_csv("data/dataset_sintomas.csv", index=False, encoding="utf-8")
print("¡Dataset 'data/dataset_sintomas.csv' generado exitosamente con 30 ejemplos traducidos y adaptados!")
