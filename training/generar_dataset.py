import pandas as pd
import os

# Definimos una lista de datos ampliada con 90 ejemplos de síntomas en español (incluyendo modismos peruanos de Lima Norte)
# asociados a su respectivo diagnóstico (falla) para entrenar el modelo de Machine Learning.
datos = [
    # --- SISTEMA DE FRENOS ---
    {"sintoma": "siento un chillido feo al frenar el carro", "falla": "Pastillas de freno desgastadas"},
    {"sintoma": "el carro chilla cuando piso el freno", "falla": "Pastillas de freno desgastadas"},
    {"sintoma": "suena como metal chocando cuando freno", "falla": "Discos de freno dañados o pastillas desgastadas al límite"},
    {"sintoma": "el pedal de freno se va hasta el fondo y se siente esponjoso", "falla": "Fuga de líquido de frenos o aire en las líneas hidráulicas"},
    {"sintoma": "el freno esta muy largo y no frena bien", "falla": "Fuga de líquido de frenos o aire en las líneas hidráulicas"},
    {"sintoma": "tengo que pisar muy fuerte el freno para que pare", "falla": "Fallo en el servo freno (booster) o pastillas cristalizadas"},
    {"sintoma": "el pedal de freno esta duro y no frena casi nada", "falla": "Fallo en el servo freno (booster) o manguera de vacío rota"},
    {"sintoma": "el carro se jala para un lado cuando freno", "falla": "Calíper de freno atascado o desgaste desigual de pastillas"},
    {"sintoma": "tiembla el timón cuando freno a velocidad alta", "falla": "Discos de freno alabeados (deformados)"},
    {"sintoma": "siento vibración en el pedal de freno al pisarlo", "falla": "Discos de freno alabeados (deformados)"},
    {"sintoma": "el freno de mano no agarra bien y se va muy arriba", "falla": "Zapatas de freno desgastadas o cable de freno de mano descalibrado"},
    {"sintoma": "se enciende la luz roja de freno en el tablero", "falla": "Bajo nivel de líquido de frenos o pastillas al límite"},
    {"sintoma": "el pedal de freno tiene demasiado juego antes de frenar", "falla": "Aire en el sistema o falta de regulación en las zapatas traseras"},
    {"sintoma": "cuando freno despacio suena como una lija en la llanta", "falla": "Pastillas de freno cristalizadas o sucias"},
    {"sintoma": "las llantas traseras se amarran cuando freno despacio", "falla": "Bombín de freno trasero pegado o cilindro dañado"},

    # --- SISTEMA DE MOTOR / ENCENDIDO ---
    {"sintoma": "el motor cascabelea cuando subo una cuesta o acelero fuerte", "falla": "Bujías desgastadas o gasolina de bajo octanaje (preignición)"},
    {"sintoma": "siento un cascabeleo en el motor al acelerar", "falla": "Bujías desgastadas o gasolina de bajo octanaje (preignición)"},
    {"sintoma": "el carro no arranca solo hace un click click al girar la llave", "falla": "Batería descargada, Bornes sulfatados o arrancador defectuoso"},
    {"sintoma": "no prende el auto no da arranque y las luces están bajas", "falla": "Batería dañada o descargada"},
    {"sintoma": "el carro demora en arrancar en las mañanas cuando esta frio", "falla": "Bujías desgastadas, filtro obstruido o bobinas débiles"},
    {"sintoma": "el motor tiembla mucho cuando esta parado en el semáforo", "falla": "Soportes de motor rotos o falla de cilindro (misfire)"},
    {"sintoma": "el auto tiembla en ralenti o cuando esta encendido pero quieto", "falla": "Soportes de motor rotos o inyectores sucios"},
    {"sintoma": "el motor se apaga de la nada cuando bajo la velocidad o freno en los rompemuelles", "falla": "Válvula IAC sucia u obstruida (control de mínimo)"},
    {"sintoma": "el motor se apaga al embragar o poner neutro", "falla": "Válvula IAC sucia u obstruida (control de mínimo)"},
    {"sintoma": "siento que el motor pierde fuerza en las subidas y tiembla", "falla": "Falla en bobinas de encendido o bujías defectuosas"},
    {"sintoma": "el motor golpea fuerte por dentro como metal chocando", "falla": "Desgaste severo de metales de biela o bancada (golpeteo interno)"},
    {"sintoma": "suena un taqueteo como máquina de coser en la tapa del motor", "falla": "Falta de lubricación en los taqués hidráulicos o válvulas descalibradas"},
    {"sintoma": "la aguja de temperatura sube al máximo y bota vapor por el capó", "falla": "Fuga de refrigerante, termostato pegado o electroventilador quemado"},
    {"sintoma": "el carro calienta rápido cuando estoy en el tráfico", "falla": "Fallo en el electroventilador o radiador obstruido"},
    {"sintoma": "se prende el testigo de aceite (aceitera roja) en el tablero", "falla": "Baja presión de aceite o falta de nivel de lubricante"},

    # --- SISTEMA DE SUSPENSIÓN Y DIRECCIÓN ---
    {"sintoma": "el timón tiembla bastante cuando voy a mas de 80 kilómetros por hora", "falla": "Llantas desalineadas, desbalanceadas o deformadas"},
    {"sintoma": "vibra la dirección del carro a alta velocidad", "falla": "Llantas desalineadas, desbalanceadas o deformadas"},
    {"sintoma": "suena un golpe seco en la llanta cuando paso por un bache o rompemuelles", "falla": "Amortiguadores reventados o bujes de suspensión gastados"},
    {"sintoma": "el carro golpea feo abajo al pasar por baches", "falla": "Amortiguadores reventados o resortes vencidos"},
    {"sintoma": "suena un clac clac fuerte al girar todo el timón para doblar", "falla": "Juntas homocinéticas (palieres) dañadas"},
    {"sintoma": "cuando doblo la esquina suena un crujido en la dirección", "falla": "Juntas homocinéticas o terminales de dirección desgastados"},
    {"sintoma": "el carro se va hacia la derecha si suelto el timón", "falla": "Falta de alineación en el eje delantero"},
    {"sintoma": "el auto se desvía solo hacia un lado al soltar la dirección", "falla": "Falta de alineación en el eje delantero"},
    {"sintoma": "la dirección se puso bien dura para estacionar y maniobrar", "falla": "Falta de líquido de dirección hidráulica o bomba de dirección dañada"},
    {"sintoma": "el timón tiene mucho juego libre antes de que las llantas giren", "falla": "Caja de dirección con desgaste o terminales de dirección flojos"},
    {"sintoma": "el carro se mece como barco en las curvas y se siente inestable", "falla": "Amortiguadores desgastados o barra estabilizadora suelta"},
    {"sintoma": "suena un chillido agudo al girar el timón completo estando quieto", "falla": "Falta de tensión en la faja de accesorios (faja del alternador/dirección)"},
    {"sintoma": "las llantas delanteras se están gastando más por los bordes internos", "falla": "Problema de camber (caída) o mala alineación"},

    # --- SISTEMA DE COMBUSTIBLE / INYECCIÓN ---
    {"sintoma": "el carro se aguanta o pierde fuerza cuando acelero", "falla": "Filtro de combustible obstruido o inyectores sucios / bomba de gasolina débil"},
    {"sintoma": "siento que el auto pierde potencia y no responde al acelerador", "falla": "Filtro de combustible obstruido o inyectores sucios / bomba de gasolina débil"},
    {"sintoma": "el carro se chupa o tironea al meter la segunda marcha", "falla": "Inyectores obstruidos o bujías deficientes"},
    {"sintoma": "el carro esta consumiendo demasiada gasolina últimamente", "falla": "Sensor de oxígeno defectuoso, filtro de aire tapado o bujías desgastadas"},
    {"sintoma": "huele mucho a gasolina dentro del carro y bota humo", "falla": "Fuga en la línea de combustible o inyectores goteando (mezcla demasiado rica)"},
    {"sintoma": "el motor tarda en responder cuando piso el acelerador a fondo", "falla": "Sensor TPS defectuoso (posición del acelerador) o cuerpo de aceleración sucio"},
    {"sintoma": "el carro tironea en marchas bajas como si se fuera a apagar", "falla": "Filtro de combustible obstruido o bobinas con fugas de corriente"},

    # --- ESCAPE Y GASES ---
    {"sintoma": "esta botando humo negro por el tubo de escape", "falla": "Mezcla rica (exceso de combustible / falla de sensor de oxígeno o sensor MAP)"},
    {"sintoma": "sale humo azul con olor a aceite quemado por el escape", "falla": "El motor consume aceite (anillos de pistón o retenes de válvula gastados)"},
    {"sintoma": "sale bastante humo blanco espeso por el tubo de escape", "falla": "Soplo de empaque de culata (ingreso de refrigerante al cilindro)"},
    {"sintoma": "el tubo de escape suena muy fuerte como si estuviera roto", "falla": "Tubo de escape roto o silenciador dañado"},
    {"sintoma": "bota humo negro en exceso y ensucia las bujías de carbón", "falla": "Mezcla rica (exceso de combustible / falla de sensor de oxígeno)"},
    {"sintoma": "suena un soplido fuerte debajo del carro al acelerar", "falla": "Empaque del múltiple de escape soplado o fisura en el tubo"},

    # --- SISTEMA ELÉCTRICO Y LUCES ---
    {"sintoma": "el testigo de la batería (batería roja) se queda prendido con el motor encendido", "falla": "El alternador no está cargando la batería correctamente"},
    {"sintoma": "las luces del tablero y los faros parpadean o bajan de intensidad al acelerar", "falla": "Regulador de voltaje del alternador defectuoso"},
    {"sintoma": "ninguna luz del carro prende, todo está completamente muerto", "falla": "Fusible principal quemado o batería totalmente dañada"},
    {"sintoma": "los limpiaparabrisas no se mueven al activarlos", "falla": "Motor de limpiaparabrisas quemado o fusible soplado"},
    {"sintoma": "el claxon o bocina no suena para nada", "falla": "Bocina quemada, fusible soplado o cinta de timón rota"},
    {"sintoma": "las luces direccionales no parpadean, se quedan fijas encendidas", "falla": "Relé de luces intermitentes (flasher) quemado"}
]

# Crear un DataFrame de Pandas
df = pd.DataFrame(datos)

# Guardar a un archivo CSV en la carpeta data
os.makedirs("data", exist_ok=True)
df.to_csv("data/dataset_sintomas.csv", index=False, encoding="utf-8")

print(f"¡Dataset 'data/dataset_sintomas.csv' generado exitosamente con {len(df)} ejemplos en español!")
