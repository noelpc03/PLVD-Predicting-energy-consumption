# message_builder.py
import json

def build_message(row):
    """
    Convierte una fila del dataframe a JSON listo para Kafka
    """
    # Convertir la fila a diccionario
    data = {
        'datetime': str(row['Datetime']),
        'global_active_power': float(row['Global_active_power']),
        'global_reactive_power': float(row['Global_reactive_power']),
        'voltage': float(row['Voltage']),
        'global_intensity': float(row['Global_intensity']),
        'sub_metering_1': float(row['Sub_metering_1']),
        'sub_metering_2': float(row['Sub_metering_2']),
        'sub_metering_3': float(row['Sub_metering_3'])
    }
    
    # Convertir a JSON
    return json.dumps(data)
