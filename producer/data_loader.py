# data_loader.py

import pandas as pd
from config import DATASET_PATH

def load_data():
    """Carga y limpia el dataset de consumo energético"""
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
