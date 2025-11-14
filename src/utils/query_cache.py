"""
Database Query Cache
Optimiza queries repetitivas con cache de 30 segundos
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Callable
import hashlib
import json

logger = logging.getLogger(__name__)


class QueryCache:
    """Cache para queries de base de datos"""
    
    def __init__(self, default_ttl: int = 30):
        """
        Args:
            default_ttl: Tiempo de vida del cache en segundos (default: 30)
        """
        self.cache = {}  # key -> {data, timestamp, ttl}
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene dato del cache si existe y no expiró
        
        Args:
            key: Clave de cache
            
        Returns:
            Dato cacheado o None si no existe/expiró
        """
        self.stats["total_queries"] += 1
        
        if key in self.cache:
            cache_entry = self.cache[key]
            age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
            
            if age < cache_entry["ttl"]:
                self.stats["hits"] += 1
                logger.debug(f"✓ Cache HIT: {key} (age: {age:.1f}s)")
                return cache_entry["data"]
            else:
                # Expiró
                del self.cache[key]
                logger.debug(f"⏱️ Cache EXPIRED: {key}")
        
        self.stats["misses"] += 1
        logger.debug(f"❌ Cache MISS: {key}")
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None):
        """
        Guarda dato en cache
        
        Args:
            key: Clave de cache
            data: Dato a cachear
            ttl: Tiempo de vida en segundos (usa default si None)
        """
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now(),
            "ttl": ttl if ttl is not None else self.default_ttl
        }
        logger.debug(f"💾 Cache SET: {key} (TTL: {self.cache[key]['ttl']}s)")
    
    def invalidate(self, key: str):
        """Invalida una entrada de cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"🗑️ Cache INVALIDATED: {key}")
    
    def clear(self):
        """Limpia todo el cache"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"🗑️ Cache limpiado: {count} entradas eliminadas")
    
    def get_or_compute(self, key: str, compute_fn: Callable, ttl: Optional[int] = None) -> Any:
        """
        Obtiene del cache o computa y guarda
        
        Args:
            key: Clave de cache
            compute_fn: Función para computar el dato si no está en cache
            ttl: Tiempo de vida en segundos
            
        Returns:
            Dato cacheado o recién computado
        """
        cached = self.get(key)
        
        if cached is not None:
            return cached
        
        # Compute
        data = compute_fn()
        self.set(key, data, ttl)
        return data
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del cache"""
        total = self.stats["total_queries"]
        hits = self.stats["hits"]
        
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        return {
            "total_queries": total,
            "cache_hits": hits,
            "cache_misses": self.stats["misses"],
            "hit_rate_percent": round(hit_rate, 2),
            "cached_entries": len(self.cache),
            "cache_size_kb": len(json.dumps(list(self.cache.keys()))) / 1024
        }
    
    def generate_key(self, *args, **kwargs) -> str:
        """
        Genera clave de cache única a partir de parámetros
        
        Args:
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Hash MD5 como clave
        """
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()


# Instancia global
db_cache = QueryCache(default_ttl=30)
