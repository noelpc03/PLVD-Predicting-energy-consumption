# app.py - Dashboard Flask para visualización de datos energéticos
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
from hive_connector import (
    get_latest_data,
    get_statistics,
    get_time_series_data,
    get_hourly_aggregates
)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')

@app.route('/api/latest')
def api_latest():
    """API endpoint para obtener los últimos registros"""
    try:
        limit = int(os.getenv('DASHBOARD_LATEST_LIMIT', '100'))
        data = get_latest_data(limit)
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistics')
def api_statistics():
    """API endpoint para obtener estadísticas agregadas"""
    try:
        stats = get_statistics()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/timeseries')
def api_timeseries():
    """API endpoint para obtener datos de series de tiempo"""
    try:
        hours = int(os.getenv('DASHBOARD_TIMESERIES_HOURS', '24'))
        data = get_time_series_data(hours)
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hourly')
def api_hourly():
    """API endpoint para obtener agregados por hora"""
    try:
        data = get_hourly_aggregates()
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'energy-dashboard'
    })

if __name__ == '__main__':
    # Puerto interno siempre 5000 (el mapeo se hace en docker-compose)
    port = int(os.getenv('DASHBOARD_PORT', '5000'))
    debug = os.getenv('DASHBOARD_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

