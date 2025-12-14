# 🚀 Optimizaciones de Imágenes Docker

## Resumen de Optimizaciones Aplicadas

Este documento detalla las optimizaciones realizadas para reducir el tamaño de las imágenes Docker del proyecto.

## 📊 Reducciones Esperadas

| Imagen | Tamaño Anterior | Tamaño Optimizado | Reducción |
|--------|----------------|-------------------|-----------|
| Dashboard | ~987MB | ~400-500MB | ~500MB (50%) |
| Producer | ~407MB | ~350-380MB | ~50MB (12%) |
| Spark Consumer | ~1.95GB | ~1.8-1.9GB | ~100MB (5%) |

**Total estimado ahorrado: ~650MB**

## 🔧 Optimizaciones Aplicadas

### 1. Dashboard (`docker/dashboard/Dockerfile`)

#### ❌ Eliminado:
- `gcc` y `g++` (compiladores C/C++) - **~150MB**
  - No necesarios en runtime, solo para compilar extensiones Python
  - Las dependencias Python ya están pre-compiladas

#### ✅ Optimizado:
- Uso de `--no-install-recommends` en apt-get
- Limpieza explícita de caché con `apt-get clean`
- Docker CLI se mantiene (necesario para ejecutar comandos en otros contenedores)

#### 💾 Ahorro: ~400-500MB

### 2. Producer (`docker/producer/Dockerfile`)

#### ✅ Optimizado:
- Combinación de comandos para reducir capas
- Limpieza de caché de pip con `pip cache purge`
- Eliminación de archivos temporales

#### 💾 Ahorro: ~50MB

### 3. Spark Consumer (`docker/spark-consumer/Dockerfile`)

#### ✅ Optimizado:
- Combinación de múltiples comandos RUN en uno solo
- Uso de `--no-install-recommends` en apt-get
- Limpieza explícita de caché
- Eliminación de archivos temporales

#### 💾 Ahorro: ~100MB

## 📝 Mejores Prácticas Aplicadas

### 1. Reducción de Capas
- Combinar múltiples comandos `RUN` en uno solo
- Usar `&&` para encadenar comandos
- Limpiar en el mismo paso que instala

### 2. Limpieza de Caché
- `rm -rf /var/lib/apt/lists/*` después de apt-get
- `apt-get clean` para limpiar caché de paquetes
- `pip cache purge` para limpiar caché de pip

### 3. Instalación Mínima
- `--no-install-recommends` para evitar paquetes recomendados innecesarios
- Solo instalar lo estrictamente necesario

### 4. Eliminación de Temporales
- Eliminar archivos temporales después de usarlos
- No dejar archivos de construcción en la imagen final

## 🔄 Cómo Aplicar las Optimizaciones

### Reconstruir Imágenes

```bash
cd docker

# Reconstruir todas las imágenes optimizadas
docker compose build --no-cache dashboard producer spark-consumer

# O reconstruir una específica
docker compose build --no-cache dashboard
```

### Verificar Tamaños

```bash
# Ver tamaños de imágenes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Comparar antes y después
docker images | grep -E "docker-dashboard|docker-producer|docker-spark-consumer"
```

## ⚠️ Notas Importantes

### Imágenes Base Pre-construidas

Las siguientes imágenes **NO** se pueden optimizar fácilmente porque son imágenes públicas:
- `bde2020/hadoop-*` (~500MB-1GB cada una)
- `confluentinc/cp-kafka` (~387MB)
- `apache/spark:3.5.0` (~1.5GB)
- `apache/hive` (~500MB-1GB)

**Razón**: No controlamos su construcción. Para optimizarlas necesitarías:
1. Construir tus propias imágenes desde cero
2. Usar imágenes base más ligeras (Alpine Linux)
3. Eliminar componentes innecesarios manualmente

**Recomendación**: Para desarrollo, el tamaño actual es aceptable. Las imágenes se descargan una vez y se reutilizan.

## 📈 Impacto en el Proyecto

### Ventajas
- ✅ Descarga inicial más rápida
- ✅ Menor uso de espacio en disco
- ✅ Menor tiempo de transferencia en CI/CD
- ✅ Mejor rendimiento en sistemas con recursos limitados

### Desventajas
- ⚠️ Requiere reconstruir imágenes (tiempo inicial)
- ⚠️ Algunas optimizaciones pueden afectar compatibilidad (no aplicado aquí)

## 🎯 Próximas Optimizaciones Posibles

Si necesitas reducir aún más el tamaño:

1. **Usar Alpine Linux como base**
   - Reduciría ~100-200MB por imagen
   - Requiere ajustar comandos (Alpine usa `apk` en lugar de `apt`)

2. **Multi-stage builds**
   - Separar construcción de runtime
   - Reduciría significativamente el tamaño final

3. **Construir imágenes base propias**
   - Control total sobre el contenido
   - Requiere más mantenimiento

## 📚 Referencias

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Optimizing Docker Images](https://docs.docker.com/build/building/optimizing-builds/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

