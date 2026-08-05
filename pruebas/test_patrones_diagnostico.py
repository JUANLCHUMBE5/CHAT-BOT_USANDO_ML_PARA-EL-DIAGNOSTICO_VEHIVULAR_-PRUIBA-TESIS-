import os
import sys

# Reconfigurar salida para soporte UTF-8 en consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.gestor_diagnostico import GestorDiagnostico

def probar_patrones():
    print("=" * 60)
    print("INICIANDO PRUEBAS DE PATRONES DE DIAGNOSTICO ESTRUCTURADOS")
    print("=" * 60)
    
    gestor = GestorDiagnostico()
    
    # Prueba 1: Consulta ambigua / incompleta (Requerimiento R1)
    print("\n--- PRUEBA 1: Captura de sintoma ambiguo ('el carro falla') ---")
    res1 = gestor.procesar_consulta_texto("el carro falla")
    print(res1)
    assert "especifique" in res1.lower() or "detalle" in res1.lower(), "Error: No se detectó la consulta ambigua."
    print("PRUEBA 1 PASADA: Solicitud de aclaracion activada correctamente.")
    
    # Prueba 2: Consulta completa con chillido de frenos
    print("\n--- PRUEBA 2: Sintoma completo ('siento un chillido feo al frenar el carro') ---")
    res2 = gestor.procesar_consulta_texto("siento un chillido feo al frenar el carro")
    print(res2)
    assert "1. Posible Falla Vehicular" in res2, "Error: Sección 1 ausente."
    assert "2. Procedimiento Técnico" in res2, "Error: Sección 2 ausente."
    assert "3. Tiempo Estimado" in res2, "Error: Sección 3 ausente."
    print("PRUEBA 2 PASADA: Formato estandarizado en 3 secciones verificado.")
    
    # Prueba 3: Consulta con Código DTC (P0300)
    print("\n--- PRUEBA 3: Consulta con Codigo DTC ('el scanner arroja el codigo P0300 cascabeleo') ---")
    res3 = gestor.procesar_consulta_texto("el scanner arroja el codigo P0300 cascabeleo")
    print(res3)
    assert "CAMBIO DE BUJÍAS" in res3 or "P0300" in res3 or "BUJIAS" in res3, "Error: No se recuperó el procedimiento RAG para P0300."
    print("PRUEBA 3 PASADA: Normalización RAG de codigos DTC OBD-II verificada.")

    # Prueba 4: Saludo / Contacto inicial ('Hola tengo problemas')
    print("\n--- PRUEBA 4: Saludo inicial ('Hola tengo problemas') ---")
    res4 = gestor.procesar_consulta_texto("Hola tengo problemas")
    print(res4)
    assert "Bienvenido a CarBot" in res4, "Error: No se interceptó el saludo inicial."
    print("PRUEBA 4 PASADA: Mensaje de bienvenida inicial interceptado con éxito.")

    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS AUTOMATIZADAS PASARON EXITOSAMENTE")
    print("=" * 60)

if __name__ == "__main__":
    probar_patrones()
