# data_loader.py

import os
import pandas as pd
from config import DATASET_PATH

def load_data():
    """Carga y limpia el dataset de consumo energético"""
    # Validar que el archivo existe antes de intentar leerlo
    if not os.path.exists(DATASET_PATH):
        error_msg = (
            f"❌ Error: El archivo del dataset no se encuentra en la ruta especificada.\n"
            f"   Ruta buscada: {os.path.abspath(DATASET_PATH)}\n"
            f"   Ruta actual de trabajo: {os.getcwd()}\n"
            f"   Por favor, verifica que el archivo existe y que la variable de entorno\n"
            f"   PRODUCER_DATASET_PATH apunta a la ubicación correcta."
        )
        raise FileNotFoundError(error_msg)
    
    # Verificar que es un archivo (no un directorio)
    if not os.path.isfile(DATASET_PATH):
        error_msg = (
            f"❌ Error: La ruta especificada no es un archivo.\n"
            f"   Ruta: {os.path.abspath(DATASET_PATH)}\n"
            f"   Por favor, verifica que la ruta apunta a un archivo válido."
        )
        raise ValueError(error_msg)
    
    # Leer dataset
    df = pd.read_csv(DATASET_PATH, sep=';', low_memory=False)

    # Normalizar valores faltantes
    df = df.replace('?', pd.NA)

    # Unificar fechas y crear columna timestamp
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)

    # Seleccionar columnas importantes
    cols = ['Datetime', 'Global_active_power', 'Global_reactive_power',
            'Voltage', 'Global_intensity', 'Sub_metering_1',
            'Sub_metering_2', 'Sub_metering_3']

    df = df[cols]

    # Convertir métricas a numérico y descartar filas corruptas
    for col in cols:
        if col != 'Datetime':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Eliminar filas con nulos tras la conversión
    df = df.dropna()

    return df
