import re

# DICCIONARIO OFICIAL DE MODISMOS Y JERGAS MECÁNICAS PERUANAS (CARABAYLLO / LIMA 2026)
DICCIONARIO_JERGA_PERUANA = {
    r"\bcaña\b": "vehiculo",
    r"\bcascabelea\b": "preignicion o falla de bujias por cascabeleo",
    r"\bcascabeleando\b": "preignicion o falla de bujias",
    r"\bchanchaea\b": "falla de encendido en cilindro misfire",
    r"\bcabecea\b": "vibracion e inestabilidad en el motor",
    r"\bse chupa\b": "pierde potencia y se aguanta al acelerar",
    r"\bse aguanta\b": "perdida de fuerza e inyeccion obstruida",
    r"\bzapatea\b": "vibracion por desbalanceo o discos de freno alabeados",
    r"\bzapateo\b": "vibracion en freno o aceleracion",
    r"\bbota vapor\b": "sobrecalentamiento e ingreso de refrigerante al motor",
    r"\bcalienta feo\b": "sobrecalentamiento de motor radiador",
    r"\bclac clac\b": "desgaste en junta homocinetica de palier",
    r"\bpedal esponjoso\b": "aire en cañerias o fuga de liquido de frenos",
    r"\bpedal largo\b": "fuga de liquido de frenos o zapatas desgastadas",
    r"\bchilla\b": "chillido de pastillas de freno o faja",
    r"\bchillido de faja\b": "faja del alternador destensada o suelta",
    r"\bhumo garzo\b": "humo azul por consumo de aceite en anillos de piston",
    r"\bhumo azul\b": "consumo de aceite por anillos de piston gastados",
    r"\bhumo negro\b": "mezcla rica demasiado combustible o sensor de oxigeno",
    r"\bhumo blanco\b": "soplo de empaque de culata o refrigerante quemado",
    r"\bplumas\b": "plumas de limpiaparabrisas",
    r"\bchapa\b": "cerradura y mecanismo de seguro de puerta",
    r"\bpestillo\b": "seguro y mecanismo de cierre de puerta",
    r"\ben minimo\b": "motor en ralenti sin acelerar",
    r"\bjalonea\b": "tirones e inestabilidad de inyectores o bujias",
    r"\bgolpe en buches\b": "amortiguador reventado o cazoleta picada",
    r"\btrancazo seco\b": "suspension o amortiguador reventado",
    r"\brasca el cambio\b": "desgaste de anillos sincronizadores en caja mecanica"
}

def normalizar_jerga_peruana(texto: str) -> str:
    """
    Traduce términos autóctonos del taller mecánico peruano a lenguaje técnico
    estandarizado para mejorar la precisión del modelo ML y la búsqueda RAG.
    """
    if not texto:
        return ""
    
    texto_procesado = texto.lower()
    
    for patron, reemplazo in DICCIONARIO_JERGA_PERUANA.items():
        texto_procesado = re.sub(patron, reemplazo, texto_procesado, flags=re.IGNORECASE)
        
    return texto_procesado

if __name__ == "__main__":
    prueba = "mi caña cascabelea en subida y el timon zapatea feo al frenar"
    print("Texto original:", prueba)
    print("Texto normalizado:", normalizar_jerga_peruana(prueba))
