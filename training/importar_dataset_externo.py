import pandas as pd
import numpy as np
import os
import sys

# Mapeador de columnas y traductor genérico para CSVs externos (Kaggle/Zenodo/GitHub)
def importar_y_mapear_dataset_externo(ruta_csv_externo: str, columna_sintoma: str, columna_falla: str):
    """
    Lee un CSV externo (ej. descargado de Kaggle o Zenodo), extrae las columnas
    de síntomas y fallas, limpia los datos y los fusiona con el dataset principal del proyecto.
    """
    if not os.path.exists(ruta_csv_externo):
        print(f"Error: No se encontró el archivo externo en '{ruta_csv_externo}'")
        return

    print(f"Leyendo dataset externo desde '{ruta_csv_externo}'...")
    df_ext = pd.read_csv(ruta_csv_externo)

    if columna_sintoma not in df_ext.columns or columna_falla not in df_ext.columns:
        print(f"Error: Las columnas '{columna_sintoma}' y/o '{columna_falla}' no existen en el CSV.")
        print(f"Columnas disponibles en el archivo: {list(df_ext.columns)}")
        return

    # Extraer y renombrar
    df_nuevo = df_ext[[columna_sintoma, columna_falla]].copy()
    df_nuevo.columns = ['sintoma', 'falla']
    df_nuevo.dropna(inplace=True)

    # Cargar dataset actual
    ruta_principal = "data/dataset_sintomas.csv"
    if os.path.exists(ruta_principal):
        df_base = pd.read_csv(ruta_principal)
        df_final = pd.concat([df_base, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo

    # Eliminar duplicados exactos
    df_final.drop_duplicates(subset=['sintoma'], inplace=True)
    df_final.to_csv(ruta_principal, index=False, encoding="utf-8")

    print("=" * 80)
    print(f"¡DATASET FUSIONADO EXITOSAMENTE!")
    print(f"-> Total de filas integradas: {len(df_nuevo)}")
    print(f"-> Total acumulado en 'data/dataset_sintomas.csv': {len(df_final)} muestras.")
    print("=" * 80)

    # Re-entrenar modelo automáticamente
    print("\nRe-entrenando el modelo de Machine Learning con los nuevos datos integrados...")
    os.system("python training/entrenar_modelo.py")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python training/importar_dataset_externo.py <ruta_csv> <columna_sintoma> <columna_falla>")
        print("Ejemplo: python training/importar_dataset_externo.py data/mi_kaggle.csv symptom fault")
    else:
        importar_y_mapear_dataset_externo(sys.argv[1], sys.argv[2], sys.argv[3])
