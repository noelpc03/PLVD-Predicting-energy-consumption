# 📊 Energy Consumption Dashboard

Dashboard web moderno y responsive para visualizar datos de consumo energético en tiempo real.

## 🎨 Características

- **Visualización en Tiempo Real**: Actualización automática cada 5 segundos
- **Gráficos Interactivos**: 
  - Evolución temporal de potencia activa
  - Distribución por hora del día
  - Desglose de sub-metering (gráfico de dona)
  - Voltaje e intensidad en tiempo real
- **Métricas Principales**: Tarjetas con estadísticas clave
- **Tabla de Últimos Registros**: Visualización tabular de datos recientes
- **Diseño Moderno**: Bootstrap 5 con gradientes y animaciones

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

El dashboard se inicia automáticamente con `docker compose`:

```bash
cd docker
docker compose up -d dashboard
```

El dashboard estará disponible en: `http://localhost:5001`

### Desarrollo Local

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (opcional):
```bash
export HIVE_METASTORE_URI=thrift://localhost:9083
export HIVE_TABLE_NAME=energy_data
export DASHBOARD_PORT=5001
```

3. Ejecutar:
```bash
python app.py
```

## 📡 API Endpoints

- `GET /` - Página principal del dashboard
- `GET /api/latest` - Últimos N registros
- `GET /api/statistics` - Estadísticas agregadas
- `GET /api/timeseries` - Datos de series de tiempo
- `GET /api/hourly` - Agregados por hora
- `GET /api/health` - Health check

## ⚙️ Configuración

Variables de entorno disponibles:

- `DASHBOARD_PORT`: Puerto del servidor (default: 5001)
- `DASHBOARD_DEBUG`: Modo debug (default: False)
- `DASHBOARD_LATEST_LIMIT`: Límite de últimos registros (default: 100)
- `DASHBOARD_TIMESERIES_HOURS`: Horas para series de tiempo (default: 24)
- `HIVE_METASTORE_URI`: URI del metastore de Hive
- `HIVE_TABLE_NAME`: Nombre de la tabla en Hive

## 🛠️ Tecnologías

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, Chart.js
- **Base de Datos**: Apache Hive
- **Visualización**: Chart.js para gráficos interactivos

## 📱 Responsive Design

El dashboard es completamente responsive y se adapta a:
- Desktop
- Tablet
- Mobile

## 🎯 Próximas Mejoras

- [ ] Filtros de fecha/hora
- [ ] Exportación de datos (CSV, PDF)
- [ ] Alertas y notificaciones
- [ ] Comparación de períodos
- [ ] Predicciones de consumo

