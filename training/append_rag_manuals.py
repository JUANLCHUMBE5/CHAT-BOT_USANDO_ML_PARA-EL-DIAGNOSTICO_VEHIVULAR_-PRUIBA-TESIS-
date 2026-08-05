import os
from src.infrastructure.motor_rag import MotorRAG

nuevos_manuales = """

=== PROCEDIMIENTO: DIAGNÓSTICO Y REEMPLAZO DE ALTERNADOR Y SISTEMA DE CARGA DE 12V (DTC P0562 / P0563 / BATERÍA NO CARGA) ===
Código de Falla Asociado: DTC P0562 (Voltaje de Sistema Bajo) / DTC P0563 (Voltaje de Sistema Alto)
Modelos Compatibles Frecuentes en Perú: Toyota Yaris/Corolla, Hyundai Accent, Kia Rio, Nissan Versa, Suzuki Swift, Changan Alsvin, DFSK
Gravedad: Alta | Tiempo Estimado de Taller: 60 minutos
Síntomas: Luz de batería encendida en tablero, luces tenues o parpadeantes, pérdida de potencia eléctrica, motor se apaga en marcha por falta de corriente.
Instrucciones paso a paso:
1. Desconectar borne negativo de la batería de 12V.
2. Mida el voltaje de batería en reposo (mínimo 12.6V) y con motor en marcha a 2000 RPM (voltaje estándar de carga del alternador: 13.8V a 14.5V). Si marca menos de 13.2V, hay falla de carga; si supera 15.0V, el regulador de voltaje está fallando.
3. Realice prueba de caída de tensión (Voltage Drop test) con multímetro entre el borne positivo B+ del alternador y el positivo de la batería (máximo 0.2V de caída) y entre carcasa del alternador y tierra del chasis (máximo 0.1V).
4. Afloje el tensor de la faja serpentina de accesorios y desmonte la correa.
5. Desconecte el arnés de control del regulador y el cable de potencia B+ retenido por tuerca de 12mm/13mm.
6. Desmonte los pernos de sujeción del alternador al bloque motor y retire la unidad.
7. Instale el alternador nuevo o reparado (puente rectificador/diodos y carbones nuevos), ajuste pernos a 45 Nm, reinstale la faja serpentina verificando la tensión y reconecte la batería.

=== PROCEDIMIENTO: DIAGNÓSTICO Y REEMPLAZO DE MOTOR DE ARRANQUE Y SOLENOIDE DE IGNICIÓN (CLIC SIN ARRANQUE / DTC P0615) ===
Código de Falla Asociado: DTC P0615 (Circuito Relé de Arranque) / Falla Mecánica Solenoide
Modelos Compatibles Frecuentes en Perú: Toyota Yaris, Hyundai Accent, Kia Rio/Picanto, Nissan Tiida/Sentra, Chevrolet Sail
Gravedad: Alta | Tiempo Estimado de Taller: 75 minutos
Síntomas: Al girar la llave o presionar botón Start solo se escucha un "clic" seco, el motor de arranque gira lento o no responde habiendo batería cargada.
Instrucciones paso a paso:
1. Verifique el estado de la batería de 12V con probador de carga (CCA) y asegúrese de que los bornes estén limpios de sulfato y ajustados a 8 Nm.
2. Compruebe la llegada de voltaje (+12V) al terminal ST (solenoide) del arrancador al dar arranque con la llave o botón.
3. Si llega voltaje pero el arrancador no gira, desmonte el conjunto: desconecte el cable negativo de la batería.
4. Desconecte el cable principal de batería (+12V B+) y el terminal del suiche de ignición en el solenoide.
5. Retire los 2 pernos pasantes de 14mm que fijan el motor de arranque a la campana de la transmisión.
6. En banco de trabajo, inspeccione los carbones (escobillas), el colector del inducido y la horquilla del bendix. Reemplace el solenoide o el arrancador completo si los contactos están fogueados.
7. Reinstale el motor de arranque, apriete pernos a 50 Nm, reconecte bornes y verifique arranque suave.

=== PROCEDIMIENTO: DIAGNÓSTICO DE CONSUMO PARÁSITO Y CAÍDA DE TENSIÓN EN BUS DE COMUNICACIÓN CAN (DESCARGA DE BATERÍA / DTC U0100) ===
Código de Falla Asociado: DTC U0100 (Pérdida de Comunicación con ECM/PCM) / Consumo Parásito Batería
Modelos Compatibles Frecuentes en Perú: Toyota Corolla, Hyundai Elantra/Tucson, Kia Cerato/Sportage, Nissan Kicks, Changan CS35
Gravedad: Media-Alta | Tiempo Estimado de Taller: 90 minutos
Síntomas: La batería se descarga completamente de un día para otro con el auto apagado, fallas intermitentes en tablero, agujas locas o códigos de red CAN bus.
Instrucciones paso a paso:
1. Espere 20 minutos con el vehículo apagado, llaves alejadas y puertas cerradas para que los módulos ECU entren en modo reposo (Sleep Mode).
2. Conecte un multímetro en función de amperaje DC en serie con el borne negativo de la batería. El consumo parásito normal debe ser menor a 50 mA (0.05 A). Si supera 100 mA, hay un consumo parásito activo.
3. Vaya retirando uno a uno los fusibles de la fusilera del vano motor y de la cabina mientras observa el multímetro hasta que el consumo caiga a niveles normales, identificando el circuito responsable (radio, alarma, rastreador GPS, módulo de carrocería BCM).
4. Para fallas de red CAN (DTC U0100): mida la resistencia entre los pines 6 (CAN High) y 14 (CAN Low) del conector OBD-II con batería desconectada. Debe marcar aproximadamente 60 Ohmios (dos resistencias de terminación de 120 Ohmios en paralelo).
5. Si la resistencia marca 120 Ohmios, uno de los módulos finales o la línea de bus CAN está interrumpida; si marca 0 Ohmios, hay cortocircuito entre líneas CAN.
6. Repare el arnés o sustituya el módulo defectuoso que impide la dormida de la red vehicular.

=== PROCEDIMIENTO: DIAGNÓSTICO Y REEMPLAZO DE MECATRÓNICA Y EMBRAGUE DOBLE EN TRANSMISIÓN DSG / DCT (DTC P0741 / P17BF / TIRONES EN CAMBIOS) ===
Código de Falla Asociado: DTC P17BF (Protección Sobrecarga Bomba Hidráulica DSG 7v DQ200) / DTC P189C (Restricción por Presión Insuficiente) / DTC P0741
Modelos Compatibles Frecuentes en Perú: Volkswagen Polo/Golf/Jetta (DSG 7v/6v), Audi A3, Hyundai Accent/Tucson DCT, Kia Cerato DCT
Gravedad: Crítica | Tiempo Estimado de Taller: 180 minutos
Síntomas: Llave inglesa o letras de marchas parpadeando en tablero, pérdida de marchas pares o impares, tirones bruscos al salir, fuga de aceite verde hidráulico bajo la mecatrónica.
Instrucciones paso a paso:
1. Conecte el escáner (VCDS / Launch) y escanee el módulo 02-Transmisión para verificar códigos de presión hidráulica (P17BF/P189C).
2. Verifique la presión del acumulador de la mecatrónica en datos en vivo: si no retiene 40-60 bar de presión y la bomba eléctrica suena continuamente, existe grieta en la carcasa o acumulador suelto.
3. Drene el aceite del grupo mecánico (75W) y el fluido sintético de la mecatrónica (Central Hidráulica CHF 11S / Febi 21829).
4. Desmonte la unidad mecatrónica del frente de la caja liberando los selectores en posición neutro mediante herramienta de palanca OEM T10407.
5. En mesa de trabajo limpia, instale la placa de refuerzo/acumulador reforzado en la carcasa mecatrónica o reemplace la mecatrónica completa.
6. Vuelva a montar la mecatrónica torqueando los pernos a 10 Nm + 90°. Rellene 1.0L de fluido hidráulico mecatrónico fresco y 1.9L de aceite de engranajes DSG.
7. Conecte el escáner y ejecute de manera obligatoria el Ajuste Básico (Basic Settings - Canal 061) escuchando las sincronizaciones y realizando la prueba de ruta de adaptación de embragues.

=== PROCEDIMIENTO: DIAGNÓSTICO Y SERVICIO A TRANSMISIÓN CONTINUAMENTE VARIABLE CVT (VARIADORES, CORREA METÁLICA Y SOLENOIDES / DTC P0701 / P0841) ===
Código de Falla Asociado: DTC P0701 (Control Transmisión CVT fuera de Rango) / DTC P0841 (Sensor Presión Fluido Transmisión CVT) / DTC P0746
Modelos Compatibles Frecuentes en Perú: Nissan Versa/Kicks/Sentra (CVT Jatco JF015E/JF011E), Toyota Corolla CVT (K313), Honda Civic CVT, Chery Tiggo CVT
Gravedad: Crítica | Tiempo Estimado de Taller: 120 minutos
Síntomas: Zumbido o silbido metálico al acelerar, sobrecalentamiento de caja en carretera, el auto no acelera al pisar el pedal (patinamiento de poleas), demora en enganchar Drive.
Instrucciones paso a paso:
1. Realizar diagnóstico con escáner e inspeccionar el contador de degradación de aceite CVT (CVT Oil Deterioration Date).
2. Medir presiones de línea en puertos de prueba hidráulicos con manómetro (Presión primaria y secundaria: 0.5 a 4.5 MPa). Presión baja indica solenoide de control de presión trabado o desgaste en poleas variadoras.
3. Levantar vehículo en plano, retirar el tapón de drenaje y desmontar el cárter de aluminio de la caja CVT.
4. Retirar y limpiar los imanes de retención de virutas. Si existen limallas gruesas de acero brillante, la correa metálica de empuje (Bosch belt) o los conos de las poleas presentan descascaramiento y requieren reparado general.
5. Reemplazar el filtro interno de succión de la bomba (filtro metálico/malla) y el filtro de papel tipo cartucho del enfriador de aceite CVT.
6. Limpiar la superficie de acople, instalar empaque nuevo de cárter y apretar pernos cruzados a 10 Nm.
7. Llenar con fluido especificado OEM (Nissan NS-3, Toyota FE, Honda HCF-2). NUNCA usar fluido ATF convencional. Calibrar nivel a 45°C por el perno rebosadero y reiniciar el contador de degradación con el escáner.

=== PROCEDIMIENTO: DIAGNÓSTICO DE CUERPO DE VÁLVULAS Y SOLENOIDES DE CAMBIO EN TRANSMISIÓN AUTOMÁTICA CON CONVERTIDOR DE PAR (DTC P0750 / P0755) ===
Código de Falla Asociado: DTC P0750 (Solenoide de Cambio A Falla Circuito) / DTC P0755 (Solenoide de Cambio B) / DTC P0740 (Embrague Convertidor TCC)
Modelos Compatibles Frecuentes en Perú: Toyota Yaris/Corolla (Caja U340E/U341E), Hyundai Accent/Elantra (A4CF1/A6MF1), Kia Rio, Chevrolet Cruze/Tracker
Gravedad: Alta | Tiempo Estimado de Taller: 100 minutos
Síntomas: Golpe brusco o "pateo" al pasar de 2da a 3ra marcha, la caja entra en modo de emergencia (Emergency limp mode / se queda trabada en 3ra marcha), códigos de solenoide eléctrico.
Instrucciones paso a paso:
1. Escanear el módulo TCU/PCM para obtener el código específico del solenoide electrohidráulico defectuoso.
2. Levantar el vehículo, drenar el fluido ATF y retirar el cárter de transmisión.
3. Desconectar el arnés de cableado interno de solenoides (arnés flexible de cinta).
4. Mida la resistencia de cada solenoide en Ohmios con multímetro directamente en el conector (Solenoides de cambio ON/OFF: 11 a 15 Ohmios; Solenoides de control lineal PWM: 5 a 7 Ohmios).
5. Retire los pernos de fijación del cuerpo de válvulas hidráulico y desmonte la unidad con cuidado de no perder los balines de chequeo de goma/acero.
6. Limpie las galerías del cuerpo de válvulas con solvente dieléctrico y reemplace el solenoide afectado o el kit completo de solenoides de cambio.
7. Instale el cuerpo de válvulas ajustando pernos al torque especificado (8 Nm), reinstale filtro nuevo de ATF, coloque cárter y rellene fluido ATF Toyota WS / Hyundai SP-IV.

=== PROCEDIMIENTO: DIAGNÓSTICO Y REEMPLAZO DE VÁLVULA DE EXPANSIÓN TÉRMICA Y FILTRO DESECANTE DE A/C (DTC B1008 / FALTA DE ENFRÍAMIENTO / PRESIONES ANORMALES) ===
Código de Falla Asociado: DTC B1008 / Presiones Manifold Fuera de Rango / Obstrucción Circuito A/C
Modelos Compatibles Frecuentes en Perú: Toyota Yaris/Corolla, Hyundai Accent/i10, Kia Rio/Sportage, Nissan Versa, Changan, DFSK
Gravedad: Media-Alta | Tiempo Estimado de Taller: 90 minutos
Síntomas: El aire acondicionado no enfría en absoluto o enfría intermitentemente, la manguera de alta presión se congela o se sobrecalienta, el manómetro de baja marca vacío (-10 inHg) y el de alta marca 250+ PSI.
Instrucciones paso a paso:
1. Recuperar el gas refrigerante R134a/R1234yf del sistema mediante estación de reciclaje de A/C.
2. Ubicar la válvula de expansión térmica (TXV) montada en la pared de fuego (firewall) de ingreso al evaporador.
3. Desconectar las tuberías de alta y baja presión de aluminio retirando las tuercas/pernos de 10mm. Reemplazar todos los empaquetados O-rings verdes de HNBR por nuevos lubricados con aceite PAG.
4. Retire los 2 pernos Allen/Torx de retención de la válvula TXV y extraiga la válvula obstruida por humedad o limallas.
5. En el condensador delantero, abra el tapón inferior roscado y sustituya el filtro desecante (cartucho de sílice en bolsa) para eliminar la humedad del circuito.
6. Instale la nueva válvula de expansión TXV, apriete pernos a 8 Nm y conecte las cañerías.
7. Realice prueba de vacío de 30 minutos (-30 inHg), compruebe estanqueidad y recargue la dosis exacta en gramos de gas R134a y 30cc de aceite refrigerante PAG 46.

=== PROCEDIMIENTO: DIAGNÓSTICO Y REEMPLAZO DE SERVOMOTORES DE COMPUERTAS HVAC Y MÓDULO RESISTOR DEL BLOWER (DTC B1082 / AIRE CALIENTE EN COPILOTO / SIN VENTILACIÓN) ===
Código de Falla Asociado: DTC B1082 (Actuador de Mezcla de Temperatura) / DTC B1086 (Actuador Modo Distribución Aire) / Falla Resistencia Blower
Modelos Compatibles Frecuentes en Perú: Toyota Corolla, Hyundai Tucson/Elantra, Kia Cerato/Sportage, Nissan Sentra/Kicks, Suzuki Vitara
Gravedad: Media | Tiempo Estimado de Taller: 60 minutos
Síntomas: El aire sale caliente por un lado del tablero y frío por el otro, se oye un chasquido o "taca taca" dentro del tablero al cambiar la temperatura, o el ventilador soplador (blower) solo funciona en la velocidad máxima (velocidad 4).
Instrucciones paso a paso:
1. Escanear el módulo Climatizador HVAC para leer DTCs de los servomotores actuadores de compuerta (Blend Door Actuator).
2. Si el ventilador interior no sopla en velocidades 1, 2 y 3 pero sí en la 4: desmonte la resistencia del blower bajo la guantera (módulo resistor de velocidad) y reemplace el fusible térmico o el módulo completo.
3. Para servomotores trabados: desmonte la tapa lateral inferior de la consola central o guantera.
4. Observe el movimiento de las palancas plásticas de la caja de distribución HVAC mientras conmuta la temperatura en el panel.
5. Retire los 3 tornillos de estrella (Phillips) de sujeción del actuador defectuoso y desconecte la ficha eléctrica.
6. Instale el servo actuador nuevo alineando los piñones plásticos en la posición de muesca neutral.
7. Ejecute el procedimiento de autocalibración de compuertas HVAC mediante el escáner o la secuencia manual de botones (mantener presionado AC + Recirculación durante 5 segundos).

=== PROCEDIMIENTO: DIAGNÓSTICO DE CONDENSADOR Y FUGAS EN EL RADIADOR DE CALEFACCIÓN / EVAPORADOR (DTC B1010 / REFRIGERANTE EN ALFOMBRA / LÍNEA AC SECA) ===
Código de Falla Asociado: DTC B1010 (Fuga Sistema de Climatización / Baja Presión de Gas)
Modelos Compatibles Frecuentes en Perú: Toyota Yaris, Hyundai Accent, Kia Rio, Nissan Versa, Chevrolet Sail, DFSK Glory
Gravedad: Media-Alta | Tiempo Estimado de Taller: 120 minutos
Síntomas: Olor dulce a anticongelante en la cabina, alfombra del piso del copiloto húmeda/pegajosa, empañamiento aceitoso en el parabrisas, pérdida continua de gas refrigerante A/C confirmada con tinte UV.
Instrucciones paso a paso:
1. Realizar inspección de fugas de A/C inyectando nitrógeno seco a 150 PSI o utilizando lámpara de luz ultravioleta (UV) y gafas amarillas para ubicar rastros de tinte fluorescente en el condensador, tuberías y evaporador.
2. Si la fuga está en el condensador (frente al radiador del motor, golpeado por piedras): vaciar sistema, retirar parachoques delantero, desacoplar cañerías de A/C, retirar condensador y colocar uno nuevo con sellos O-ring nuevos.
3. Si existe fuga de anticongelante por el radiador de calefacción (Heater Core): drenar el refrigerante del motor (coolant), desacoplar las mangueras de agua en la pared de fuego.
4. Desmontar la consola central y la estructura del tablero (dash replacement) si el modelo lo requiere para extraer el radiador de calefacción dañado de la caja climática.
5. Reemplazar el radiador de calefacción, armar la caja climática, reconectar mangueras de refrigerante, rellenar refrigerante de motor 50/50 y purgar el sistema de enfriamiento del motor.
6. Efectuar prueba de vacío y recarga de refrigerante R134a al A/C probando el funcionamiento del climatizador a máxima potencia de frío y calor.

=== PROCEDIMIENTO: DIAGNÓSTICO Y REEMPLAZO DEL MÓDULO DE CONTROL ELECTRÓNICO ABS/ESP Y UNIDAD HIDRÁULICA HCU (DTC C0110 / C0265 / SIN COMUNICACIÓN CON ABS) ===
Código de Falla Asociado: DTC C0110 (Falla Circuito Motor Bomba ABS) / DTC C0265 (Falla Relé de Módulo EBCM/ABS) / DTC U0121 (Pérdida Comunicación con ABS)
Modelos Compatibles Frecuentes en Perú: Toyota Yaris/Corolla, Hyundai Accent/Tucson, Kia Rio/Sportage, Nissan Versa/Sentra, Chevrolet Tracker
Gravedad: Crítica | Tiempo Estimado de Taller: 120 minutos
Síntomas: Testigos de ABS, ESP/VSC y Freno de Mano encendidos fijamente en tablero, el motor de la bomba ABS se queda encendido continuamente incluso con auto apagado o el pedal de freno no tiene asistencia ABS.
Instrucciones paso a paso:
1. Realizar escaneo al sistema EBCM/ABS. Verificar fusibles de alta corriente del ABS (40A/60A) en la caja de fusibles del motor y la masa/tierra principal del módulo.
2. Medir llegada de +12V en los pines de potencia del arnés multipin del ABS. Si hay voltaje y masa correcta pero marca DTC C0110/C0265 o no hay comunicación, la unidad electrónica EBCM o la bomba interna están averiadas.
3. Drenar el líquido de frenos del depósito principal.
4. Marcar e identificar las 6 tuberías rígidas de freno metálicas acopladas a la unidad hidráulica HCU (2 de cilindro maestro y 4 para cada rueda).
5. Aflojar los racores roscados de las cañerías con llave para tuberías de 10mm/11mm y desacoplar las líneas.
6. Desmontar los 3 pernos de sujeción del módulo ABS al chasis y retirar la unidad HCU/EBCM completa.
7. Instalar el nuevo módulo ABS, ajustar racores de cañerías a 16 Nm, conectar el arnés eléctrico, realizar codificación VIN de la ECU ABS con escáner e iniciar el protocolo de purga electrónica de electroválvulas.

=== PROCEDIMIENTO: CALIBRACIÓN DEL SENSOR DE ÁNGULO DE DIRECCIÓN (SAS) Y CONTROL DE ESTABILIDAD ESP/VSC (DTC C1231 / C1210 / TABLERO ESP ENCENDIDO) ===
Código de Falla Asociado: DTC C1231 (Falla Circuito Sensor Ángulo Dirección SAS) / DTC C1210 (Sensor Ángulo Dirección No Calibrado) / DTC C1515
Modelos Compatibles Frecuentes en Perú: Toyota Corolla/Yaris, Hyundai Elantra/Tucson, Kia Cerato/Sportage, Nissan Qashqai, Suzuki Swift
Gravedad: Alta | Tiempo Estimado de Taller: 45 minutos
Síntomas: Luz de advertencia de ESP / VSC / Slip encendida permanentemente en el tablero tras realizar una alineación de ruedas, desmontar la columna de dirección o cambiar la batería.
Instrucciones paso a paso:
1. Verificar que los neumáticos tengan la presión de aire correcta recomendada por el fabricante y que la suspensión no presente juego mecánico en rótulas ni terminales.
2. Estacionar el vehículo en una superficie completamente plana y nivelada.
3. Posicionar las ruedas delanteras perfectamente rectas hacia adelante y centrar la posición visual del volante (posición 12 en punto).
4. Conectar el escáner al puerto OBD-II y seleccionar el módulo ESP / VSC / ABS.
5. Ingresar a la sección de Funciones Especiales / Adaptación y seleccionar "Calibración de Punto Cero Sensor SAS" (Steering Angle Sensor Zero Point Calibration).
6. Siga la secuencia en pantalla: mantener el auto estático sin mover el volante ni tocar pedales durante 10 segundos, apagar el contacto (Key OFF) 15 segundos y volver a encender (Key ON).
7. Comprobar en el flujo de datos en vivo que el valor del ángulo de dirección marque 0.0° con el volante centrado. Borrar códigos DTC y realizar prueba de manejo comprobando que la luz ESP se apague.

=== PROCEDIMIENTO: PURGA ELECTRÓNICA Y REEMPLAZO DE ELECTROVÁLVULAS DEL MÓDULO ABS CON ESCÁNER DIAGNÓSTICO (DTC C0020 / C0082 / PEDAL DURO BAJO ACTIVACIÓN ABS) ===
Código de Falla Asociado: DTC C0020 (Circuito Motor Bomba ABS Fuera de Rango) / DTC C0082 (Luz Indique Falla Frenos)
Modelos Compatibles Frecuentes en Perú: Toyota Yaris, Hyundai Accent, Kia Rio, Nissan Versa, Chevrolet Sail, DFSK
Gravedad: Crítica | Tiempo Estimado de Taller: 60 minutos
Síntomas: Pedal de freno se siente esponjoso únicamente al activarse el ABS, o el pedal se va al fondo tras intervenir cañerías hidráulicas debido a aire atrapado en la cámara interna del bloque de electroválvulas HCU.
Instrucciones paso a paso:
1. Conectar la máquina de purga por presión en el depósito de freno a 1.5 bar o asegurar que el depósito de líquido de frenos se mantenga lleno con DOT 4 sintético.
2. Conectar el escáner automotriz profesional al puerto OBD-II y entrar al módulo ABS.
3. Seleccionar la función "Purga de Servicio ABS" / "Automated ABS Bleed Protocol".
4. El escáner solicitará abrir el niple de purga de la rueda Trasera Derecha. Abrir el niple 1/4 de vuelta con llave de 8mm/10mm y presionar "Continuar" en el escáner.
5. La bomba del ABS y las electroválvulas internas se ciclo-activarán electrónicamente durante 60 segundos expulsando el aire atrapado en los acumuladores internos de la HCU hacia la rueda. Cierre el niple al finalizar el ciclo.
6. Repita la secuencia guiada por el escáner para las ruedas Trasera Izquierda, Delantera Derecha y Delantera Izquierda.
7. Verifique la firmeza del pedal de freno. El pedal debe sentirse completamente rígido y sin recorrido excesivo.

=== PROCEDIMIENTO: DIAGNÓSTICO Y REEMPLAZO DEL SENSOR DE PAR/TORQUE Y MOTOR ELECTRÓNICO EPS DE COLUMNA (DTC C1515 / C1525 / TIMÓN RÍGIDO CON VOLANTE DESVIADO) ===
Código de Falla Asociado: DTC C1515 (Sensor de Torque Punto Cero No Inicializado) / DTC C1525 (Falla Circuito Sensor de Torque EPS) / DTC C1511
Modelos Compatibles Frecuentes en Perú: Toyota Corolla/Yaris, Hyundai Accent/i10, Kia Rio/Picanto, Nissan Sentra, Suzuki Swift
Gravedad: Alta | Tiempo Estimado de Taller: 90 minutos
Síntomas: El timón se pone extremadamente duro como si no tuviera asistencia, la luz de advertencia P/S (Power Steering) parpadea o se enciende en rojo en el tablero, asistencia desigual (suave hacia la izquierda y dura hacia la derecha).
Instrucciones paso a paso:
1. Conectar el escáner de diagnóstico e ingresar al módulo EPS (Electric Power Steering).
2. Comprobar los valores en tiempo real de los sensores de torque principal (TRQ1) y secundario (TRQ2): en reposo ambos deben marcar aproximadamente 2.5V (o diferencia entre ambos < 0.15V).
3. Verificar la llegada de alimentación principal (+12V permanente) al módulo de control EPS proveniente del fusible de alta capacidad (60A/80A EPS) ubicado en el vano motor.
4. Si el sensor de torque interno de la columna presenta cortocircuito o diferencia de voltaje constante, desmonte la columna de dirección inferior retirando el volante (desconectar batería 15 min antes para desactivar Airbag), las cubiertas plásticas y la junta cardánica.
5. Desmonte el servomotor eléctrico asistido o el conjunto de columna con sensor de par integrado.
6. Instale la nueva columna/motor EPS torqueando pernos de sujeción a 30 Nm.
7. Reconecte la batería, realice de manera obligatoria la Calibración de Punto Cero del Sensor de Torque EPS con escáner y verifique la suavidad de giro en ambas direcciones.

=== PROCEDIMIENTO: CALIBRACIÓN DE PUNTO CERO Y REAPRENDIZAJE DEL SISTEMA DE DIRECCIÓN ASISTIDA EPS CON ESCÁNER (DTC C1555 / ERROR DE CALIBRACIÓN EPS) ===
Código de Falla Asociado: DTC C1555 (Falla Módulo ECU EPS / Error Calibración) / DTC C1515
Modelos Compatibles Frecuentes en Perú: Toyota Yaris/Corolla/RAV4, Hyundai Accent/Elantra, Kia Rio/Cerato, Nissan Kicks
Gravedad: Alta | Tiempo Estimado de Taller: 35 minutos
Síntomas: Luz de advertencia P/S encendida en el tablero tras desconectar la batería de 12V, realizar trabajos de suspensión o sustituir el módulo ECU de la EPS.
Instrucciones paso a paso:
1. Asegurar que la batería tenga un voltaje estable superior a 12.5V (conectar cargador/mantenedor de batería si es necesario).
2. Colocar las ruedas delanteras apoyadas sobre el suelo plano perfectamente derechas y centradas.
3. Conectar el escáner automotriz e ingresar a EPS -> Funciones Especiales -> "Calibración del Sensor de Par / Torque Sensor Calibration".
4. Seleccionar "Borrado de Datos de Calibración Anterior" (Clear Calibration Data).
5. Seleccionar "Aprendizaje de Punto Cero" (Zero Point Calibration). Durante el procedimiento, NO tocar el volante ni aplicar fuerza alguna sobre el timón.
6. Seguir las instrucciones de ciclaje de ignición: apagar el switch (Key OFF) por 10 segundos, encender el switch (Key ON) sin arrancar el motor y esperar la confirmación de "Procedimiento Exitoso" en la pantalla del escáner.
7. Borrar los códigos de falla DTC almacenados, encender el motor y comprobar que la luz de dirección asistida (P/S) se apague.

=== PROCEDIMIENTO: DIAGNÓSTICO Y REEMPLAZO DE CAJA DE DIRECCIÓN CREMALLERA ELECTRÓNICA Y ACOPLE FLEXIBLE (CHILLIDO / JUEGO EN CREMALLERA / DTC C1532) ===
Código de Falla Asociado: DTC C1532 (Falla Mecánica / Acoplamiento Motor EPS) / Ruido Mecánico en Cremallera
Modelos Compatibles Frecuentes en Perú: Hyundai Accent/i10/Elantra, Kia Rio/Picanto/Cerato, Toyota Yaris, Nissan Versa
Gravedad: Media-Alta | Tiempo Estimado de Taller: 120 minutos
Síntomas: Golpeteo seco o chasquido tipo "taca taca" metálico al girar el timón en terreno empedrado o al maniobrar para estacionar, juego libre excesivo en el volante, desalineación.
Instrucciones paso a paso:
1. Para ruido proveniente de la columna EPS en modelos Hyundai/Kia: desmonte la parte inferior de la columna de dirección EPS bajo el tablero para acceder al servomotor.
2. Retire los 3 pernos de fijación del servomotor de la columna y extraiga el acople flexible de goma en forma de estrella (Flexible Steering Coupler). Si los dientes de goma están desgastados o pulverizados, instale el nuevo acople de poliuretano reforzado y vuelva a armar el servomotor.
3. Para holgura en la caja de dirección cremallera asistida (Rack & Pinion): levante el auto, retire las ruedas delanteras y desacople los terminales de dirección de los manguetas.
4. Desmonte las abrazaderas de la barra estabilizadora y baje el subchasis cuna del motor retirando los pernos principales.
5. Desmonte la caja cremallera de dirección desacoplando el nudo cardánico de la columna.
6. Instale la nueva caja cremallera de dirección EPS, torquee pernos de sujeción al subchasis a 90 Nm, oriente los axiales y terminales de dirección.
7. Arme el conjunto, realice la alineación computarizada de dirección e inicie la calibración del sensor de punto cero de dirección EPS con escáner.
"""

ruta_txt = "manuales_taller/manual_procedimientos.txt"
with open(ruta_txt, "a", encoding="utf-8") as f:
    f.write(nuevos_manuales)

print("15 nuevos manuales de taller anexados exitosamente!")

print("\nRe-indexando la base RAG vectorial FAISS...")
rag = MotorRAG()
print(f"-> Base RAG actualizada: {len(rag.titulos)} procedimientos técnicos indexados en FAISS.")
