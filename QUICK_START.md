# 📚 RESUMEN COMPLETO - Guía Rápida de Instalación

## 🎯 Para Empezar (Si no tienes nada instalado)

### ✅ **Lo que TIENES:**
- ✅ El proyecto descargado
- ✅ El dataset (household_power_consumption.txt)
- ✅ Una computadora con Ubuntu/Linux

### ❌ **Lo que te FALTA:**
- ❌ Docker
- ❌ Docker Compose

---

## 📝 PASOS EXACTOS PARA TI

### **PASO 1: Instalar Docker (10 minutos)**

Abre una terminal y ejecuta estos comandos uno por uno:

```bash
# 1. Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias
sudo apt install -y ca-certificates curl gnupg lsb-release

# 3. Agregar repositorio de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 5. Verificar instalación
sudo docker --version

# Deberías ver algo como: Docker version 24.0.7, build afdd53b
```

**✅ Docker instalado!**

---

### **PASO 2: Configurar permisos (2 minutos)**

Para no tener que usar `sudo` cada vez:

```bash
# Agregar tu usuario al grupo docker
sudo usermod -aG docker $USER

# Aplicar cambios
newgrp docker

# Verificar que funciona (SIN sudo)
docker ps
```

Si ves una tabla vacía (sin errores), ¡funciona! ✅

---

### **PASO 3: Verificar requisitos (1 minuto)**

```bash
# Ir a tu proyecto
cd "/home/noel/Disco D/4to_Anno/BigData/PLVD-Predicting-energy-consumption"

# Ejecutar verificación
./check-requirements.sh
```

**Deberías ver:**
```
✅ Docker instalado (versión X.X.X)
✅ Docker está corriendo
✅ Docker Compose instalado
✅ RAM suficiente
✅ Dataset encontrado
...
✅ ¡Perfecto! Tu sistema está listo.
```

---

### **PASO 4: Iniciar el proyecto (5 minutos)**

```bash
# Ejecutar script de inicio
./start.sh
```

Este script hará automáticamente:
- ✅ Construir las imágenes Docker (primera vez: ~10 min)
- ✅ Iniciar Kafka y HDFS
- ✅ Configurar directorios
- ✅ Iniciar Producer y Consumer

**Salida esperada:**
```
🚀 PLVD - Inicio Rápido
========================================
✅ Docker instalado
✅ Dataset encontrado
🔧 Construyendo imágenes Docker...
✅ Imágenes construidas
🚀 Iniciando servicios...
✅ Kafka está listo
✅ NameNode está listo
✅ Producer está enviando datos
✅ Consumer está procesando datos
========================================
✅ ¡Sistema iniciado correctamente!
```

---

### **PASO 5: Verificar que funciona (2 minutos)**

#### Opción 1: Ver logs en terminal

```bash
# Terminal 1: Ver Producer
docker logs -f producer
# Debes ver: 📤 Enviado: {"datetime": "...", ...}

# Terminal 2: Ver Consumer (abre otra terminal)
docker logs -f spark-consumer
# Debes ver: ✅ Consumer iniciado correctamente
```

#### Opción 2: Ver en navegador

1. **HDFS**: http://localhost:9870
   - Utilities → Browse the file system
   - Navegar a `/user/amalia/energy_data/streaming/`
   - Después de 2-3 minutos verás carpetas con datos

2. **Spark UI**: http://localhost:4040
   - Ver jobs en ejecución
   - Streaming tab muestra estadísticas

---

### **PASO 6: Consultar datos (Opcional)**

Después de 5 minutos de ejecución:

```bash
# Ver archivos en HDFS
docker exec namenode hdfs dfs -ls /user/amalia/energy_data/streaming/

# Entrar a Spark SQL
docker exec -it spark-consumer /opt/spark/bin/spark-sql --master local
```

Dentro de Spark SQL:
```sql
-- Ver registros
SELECT * FROM energy_data LIMIT 10;

-- Consumo promedio por año
SELECT year, AVG(global_active_power) 
FROM energy_data 
GROUP BY year;

-- Salir
EXIT;
```

---

## 🛑 Para Detener Todo

```bash
cd docker
docker compose down
```

Para eliminar TODO (incluyendo datos):
```bash
docker compose down -v
```

---

## 🐛 Si algo falla...

### Error: "Cannot connect to Docker daemon"
```bash
sudo systemctl start docker
```

### Error: "Port already in use"
```bash
# Ver qué usa el puerto 9092 (ejemplo)
sudo lsof -i :9092

# Matar proceso
sudo kill -9 <PID>
```

### Error: Producer no envía datos
```bash
# Ver logs
docker logs kafka
docker logs producer

# Reiniciar
docker compose restart kafka
sleep 30
docker compose restart producer
```

### Error: No hay espacio en disco
```bash
# Limpiar Docker (imágenes y contenedores viejos)
docker system prune -a
```

---

## 📊 Tiempos Estimados

| Actividad | Primera Vez | Siguientes Veces |
|-----------|-------------|------------------|
| Instalar Docker | 10 min | - |
| Construir imágenes | 10 min | 2 min |
| Iniciar servicios | 3 min | 2 min |
| Ver primeros datos | 2 min | 2 min |
| **TOTAL** | **~25 min** | **~6 min** |

---

## ✅ Checklist Rápido

Marca cuando completes cada paso:

- [ ] Docker instalado: `docker --version`
- [ ] Permisos configurados: `docker ps` (sin sudo)
- [ ] Requisitos verificados: `./check-requirements.sh`
- [ ] Sistema iniciado: `./start.sh`
- [ ] Producer funcionando: `docker logs producer | grep Enviado`
- [ ] Consumer funcionando: `docker logs spark-consumer | grep "Consumer iniciado"`
- [ ] HDFS accesible: http://localhost:9870
- [ ] Datos en HDFS: `docker exec namenode hdfs dfs -ls /user/amalia/`

---

## 📁 Archivos Importantes

- **INSTALLATION_GUIDE.md** ← Guía detallada completa
- **README.md** ← Descripción del proyecto
- **check-requirements.sh** ← Verifica requisitos
- **start.sh** ← Inicia todo automáticamente
- **docker/FIXES_APPLIED.md** ← Correcciones aplicadas

---

## 🎓 Flujo de Datos (Recapitulación)

```
1. Dataset (2M registros)
   ↓
2. Producer (Python) lee CSV y envía a Kafka cada 5s
   ↓
3. Kafka almacena mensajes en topic "energy_stream"
   ↓
4. Consumer (Spark) lee de Kafka cada 60s
   ↓
5. Spark transforma datos (limpia, valida, particiona)
   ↓
6. HDFS almacena en formato Parquet
   ↓
7. Hive crea tabla SQL sobre los datos
   ↓
8. Análisis y consultas
```

---

## 🆘 Soporte Rápido

**Problema más común:** "No veo datos en HDFS"
- ✅ Espera 2-3 minutos (el Consumer procesa cada 60s)
- ✅ Verifica Producer: `docker logs producer`
- ✅ Verifica Consumer: `docker logs spark-consumer`

**Segundo problema más común:** "Docker no inicia"
- ✅ Verifica memoria disponible: `free -h` (necesitas >6GB libres)
- ✅ Reinicia Docker: `sudo systemctl restart docker`
- ✅ Limpia espacio: `docker system prune`

---

## 🚀 ¡Estás listo!

Si llegaste hasta aquí, deberías tener el sistema completo funcionando.

**Próximos pasos:**
1. Deja correr el sistema 10-15 minutos
2. Explora HDFS en http://localhost:9870
3. Ejecuta consultas SQL con Spark
4. Revisa el código en `producer/` y `consumer/`

---

Última actualización: 2025-10-28
Por cualquier duda, revisa los logs: `docker logs <nombre-contenedor>`
