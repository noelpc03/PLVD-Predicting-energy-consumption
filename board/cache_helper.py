# cache_helper.py - Sistema de caché simple para reducir queries repetidas
import time
from typing import Optional, Any, Callable
from functools import wraps

# Caché simple en memoria con TTL (Time To Live)
_cache: dict = {}
_cache_timestamps: dict = {}

# TTL por defecto: 60 segundos
DEFAULT_TTL = 60

def get_cached(key: str, ttl: int = DEFAULT_TTL) -> Optional[Any]:
    """
    Obtiene un valor del caché si existe y no ha expirado
    
    Args:
        key: Clave del caché
        ttl: Tiempo de vida en segundos
    
    Returns:
        Valor en caché o None si no existe o expiró
    """
    if key in _cache:
        if time.time() - _cache_timestamps[key] < ttl:
            return _cache[key]
        else:
            # Expiró, eliminar
            del _cache[key]
            del _cache_timestamps[key]
    return None

def set_cached(key: str, value: Any) -> None:
    """
    Guarda un valor en el caché
    
    Args:
        key: Clave del caché
        value: Valor a guardar
    """
    _cache[key] = value
    _cache_timestamps[key] = time.time()

def clear_cache(key: Optional[str] = None) -> None:
    """
    Limpia el caché
    
    Args:
        key: Si se proporciona, solo limpia esa clave. Si es None, limpia todo.
    """
    if key is None:
        _cache.clear()
        _cache_timestamps.clear()
    else:
        _cache.pop(key, None)
        _cache_timestamps.pop(key, None)

def cached(ttl: int = DEFAULT_TTL):
    """
    Decorador para cachear resultados de funciones
    
    Usage:
        @cached(ttl=60)
        def my_function():
            return expensive_operation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear clave única basada en función y argumentos
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Intentar obtener del caché
            cached_value = get_cached(cache_key, ttl)
            if cached_value is not None:
                return cached_value
            
            # Ejecutar función y guardar resultado
            result = func(*args, **kwargs)
            set_cached(cache_key, result)
            return result
        
        return wrapper
    return decorator

