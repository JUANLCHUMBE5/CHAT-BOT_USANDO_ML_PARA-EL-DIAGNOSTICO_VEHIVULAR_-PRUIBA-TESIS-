import sys
from src.infrastructure.modelo_ml import ModeloML
from src.config import settings

def main():
    print("=" * 70)
    print("🚗 SISTEMA DE PRUEBA INTERACTIVA DE DIAGNÓSTICO VEHICULAR")
    print("=" * 70)
    print("Cargando modelo de Machine Learning entrenado...")

    try:
        modelo = ModeloML()
        print(f"¡Modelo cargado exitosamente!")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        return

    print("=" * 70)
    print("Escribe el síntoma que notas en el auto para predecir la falla.")
    print("Escribe 'salir' para finalizar.")
    print("=" * 70)

    while True:
        try:
            entrada = input("\nIntroduce síntoma: ")
        except (KeyboardInterrupt, EOFError):
            break

        if entrada.lower().strip() == 'salir':
            break

        if not entrada.strip():
            continue

        falla, confianza = modelo.predecir(entrada)

        print("-" * 60)
        print(f"SÍNTOMA INGRESADO: \"{entrada}\"")
        print(f"DIAGNÓSTICO PREDICHO: {falla}")
        print(f"NIVEL DE CONFIANZA: {confianza:.2f}%")
        print("-" * 60)

if __name__ == "__main__":
    main()
