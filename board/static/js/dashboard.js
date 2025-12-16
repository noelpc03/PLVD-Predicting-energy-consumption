// dashboard.js - JavaScript para el dashboard de energía

// Configuración
const UPDATE_INTERVAL = 30000; // 30 segundos - reducido para evitar saturación
const API_BASE = '';
const QUERY_DELAY = 2000; // 2 segundos entre queries para evitar saturación

// Variables globales para los gráficos
let timeSeriesChart = null;
let hourlyChart = null;
let subMeteringChart = null;
let voltageIntensityChart = null;

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function () {
    initializeCharts();
    loadData();
    setInterval(loadData, UPDATE_INTERVAL);
});

// Inicializar gráficos
function initializeCharts() {
    // Time Series Chart
    const timeSeriesCtx = document.getElementById('timeSeriesChart').getContext('2d');
    timeSeriesChart = new Chart(timeSeriesCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Potencia Activa (kW)',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Potencia (kW)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Tiempo'
                    }
                }
            }
        }
    });

    // Hourly Chart
    const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
    hourlyChart = new Chart(hourlyCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Potencia Promedio (kW)',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Potencia (kW)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Hora del día'
                    }
                }
            }
        }
    });

    // Sub-metering Chart
    const subMeteringCtx = document.getElementById('subMeteringChart').getContext('2d');
    subMeteringChart = new Chart(subMeteringCtx, {
        type: 'doughnut',
        data: {
            labels: ['Sub-metering 1', 'Sub-metering 2', 'Sub-metering 3'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return context.label + ': ' + context.parsed.toFixed(2) + ' kW';
                        }
                    }
                }
            }
        }
    });

    // Voltage & Intensity Chart
    const voltageIntensityCtx = document.getElementById('voltageIntensityChart').getContext('2d');
    voltageIntensityChart = new Chart(voltageIntensityCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Voltaje (V)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    yAxisID: 'y',
                    tension: 0.4
                },
                {
                    label: 'Intensidad (A)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    yAxisID: 'y1',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Tiempo'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Voltaje (V)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Intensidad (A)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

// Cargar todos los datos (secuencial con delays para evitar saturación)
async function loadData() {
    try {
        // Cargar en secuencia con delays para evitar saturación de Spark
        await loadStatistics();
        await sleep(QUERY_DELAY);

        await loadTimeSeries();
        await sleep(QUERY_DELAY);

        await loadHourly();
        await sleep(QUERY_DELAY);

        await loadLatestData();

        updateLastUpdateTime();
        updateStatus(true);
    } catch (error) {
        console.error('Error cargando datos:', error);
        updateStatus(false);
    }
}

// Función auxiliar para delays
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Cargar estadísticas
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE}/api/statistics`);
        const result = await response.json();

        if (result.success && result.data && Object.keys(result.data).length > 0) {
            const stats = result.data;

            // Actualizar tarjetas de estadísticas
            document.getElementById('stat-avg-power').textContent =
                (stats.avg_active_power !== undefined && stats.avg_active_power !== null)
                    ? stats.avg_active_power.toFixed(2) : '--';
            document.getElementById('stat-avg-voltage').textContent =
                (stats.avg_voltage !== undefined && stats.avg_voltage !== null)
                    ? stats.avg_voltage.toFixed(1) : '--';
            document.getElementById('stat-avg-intensity').textContent =
                (stats.avg_intensity !== undefined && stats.avg_intensity !== null)
                    ? stats.avg_intensity.toFixed(2) : '--';
            document.getElementById('stat-total-records').textContent =
                (stats.total_records !== undefined && stats.total_records !== null)
                    ? stats.total_records.toLocaleString() : '--';
        } else {
            console.warn('Statistics endpoint returned empty data');
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

// Cargar series de tiempo
async function loadTimeSeries() {
    try {
        const response = await fetch(`${API_BASE}/api/timeseries`);
        const result = await response.json();

        if (result.success && result.data && result.data.length > 0) {
            const data = result.data;
            const labels = data.map(d => d.datetime);
            const powerData = data.map(d => d.avg_active_power || 0);

            timeSeriesChart.data.labels = labels;
            timeSeriesChart.data.datasets[0].data = powerData;
            timeSeriesChart.update('none');

            // Actualizar voltaje e intensidad
            const voltageData = data.map(d => d.avg_voltage || 0);
            const intensityData = data.map(d => d.avg_intensity || 0);

            voltageIntensityChart.data.labels = labels;
            voltageIntensityChart.data.datasets[0].data = voltageData;
            voltageIntensityChart.data.datasets[1].data = intensityData;
            voltageIntensityChart.update('none');
        }
    } catch (error) {
        console.error('Error cargando series de tiempo:', error);
    }
}

// Cargar datos por hora
async function loadHourly() {
    try {
        const response = await fetch(`${API_BASE}/api/hourly`);
        const result = await response.json();

        if (result.success && result.data && result.data.length > 0) {
            const data = result.data;
            const labels = data.map(d => `${d.hour}:00`);
            const powerData = data.map(d => d.avg_active_power || 0);

            hourlyChart.data.labels = labels;
            hourlyChart.data.datasets[0].data = powerData;
            hourlyChart.update('none');
        } else {
            console.warn('Hourly endpoint returned empty data');
            // Mantener gráfico vacío en lugar de ocultarlo
        }
    } catch (error) {
        console.error('Error cargando datos por hora:', error);
    }
}

// Cargar últimos registros
async function loadLatestData() {
    try {
        const response = await fetch(`${API_BASE}/api/latest`);
        const result = await response.json();

        if (result.success && result.data && result.data.length > 0) {
            const tbody = document.getElementById('latest-data-table');
            tbody.innerHTML = result.data.map(row => `
                <tr class="fade-in">
                    <td>${row.datetime || '--'}</td>
                    <td>${row.global_active_power ? row.global_active_power.toFixed(3) : '--'}</td>
                    <td>${row.global_reactive_power ? row.global_reactive_power.toFixed(3) : '--'}</td>
                    <td>${row.voltage ? row.voltage.toFixed(2) : '--'}</td>
                    <td>${row.global_intensity ? row.global_intensity.toFixed(2) : '--'}</td>
                    <td>${row.sub_metering_1 ? row.sub_metering_1.toFixed(1) : '--'}</td>
                    <td>${row.sub_metering_2 ? row.sub_metering_2.toFixed(1) : '--'}</td>
                    <td>${row.sub_metering_3 ? row.sub_metering_3.toFixed(1) : '--'}</td>
                </tr>
            `).join('');

            // Actualizar sub-metering chart con los últimos datos
            if (result.data.length > 0) {
                const latest = result.data[0];
                // Calcular totales de sub-metering de los últimos registros para mejor visualización
                const totals = result.data.reduce((acc, row) => {
                    acc[0] += (row.sub_metering_1 || 0);
                    acc[1] += (row.sub_metering_2 || 0);
                    acc[2] += (row.sub_metering_3 || 0);
                    return acc;
                }, [0, 0, 0]);

                updateSubMeteringChart(totals);
            }
        }
    } catch (error) {
        console.error('Error cargando últimos registros:', error);
    }
}

// Actualizar gráfico de sub-metering
function updateSubMeteringChart(data) {
    subMeteringChart.data.datasets[0].data = data;
    subMeteringChart.update('none');
}

// Actualizar tiempo de última actualización
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('es-ES');
    document.getElementById('last-update').textContent = `Última actualización: ${timeString}`;
}

// Actualizar estado
function updateStatus(online) {
    const badge = document.getElementById('status-badge');
    if (online) {
        badge.className = 'badge bg-success me-2';
        badge.innerHTML = '<i class="bi bi-circle-fill"></i> Online';
    } else {
        badge.className = 'badge bg-danger me-2';
        badge.innerHTML = '<i class="bi bi-circle-fill"></i> Offline';
    }
}

