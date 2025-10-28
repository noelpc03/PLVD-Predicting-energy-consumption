# data_loader.py

import pandas as pd
from config import DATASET_PATH

def load_data():
    """Carga y limpia el dataset de consumo energético"""
    # Leer dataset
    df = pd.read_csv(DATASET_PATH, sep=';', low_memory=False)

    # Eliminar filas con nulos
    df = df.dropna()

    # Unificar fechas y crear columna timestamp
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)

    # Seleccionar columnas importantes
    df = df[['Datetime', 'Global_active_power', 'Global_reactive_power',
             'Voltage', 'Global_intensity', 'Sub_metering_1',
             'Sub_metering_2', 'Sub_metering_3']]

    return df
