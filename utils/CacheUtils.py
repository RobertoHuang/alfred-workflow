from utils.LogUtils import LogUtils


class SingleCache:
    """
    单例缓存类
    使用单例模式确保全局只有一个缓存实例
    """
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingleCache, cls).__new__(cls)
        return cls._instance

    @property
    def cache(self):
        """获取缓存字典"""
        return self._cache

    def clear(self):
        """清空缓存"""
        self._cache.clear()


# 全局单例实例
_single_cache = SingleCache()


def get_cache():
    """
    获取缓存字典
    
    返回:
        缓存字典对象
    """
    return _single_cache.cache


def put(key, value):
    """
    将键值对存入缓存
    
    参数:
        key: 缓存键
        value: 缓存值
    """
    cache = get_cache()
    cache[key] = value
    LogUtils.info(f'CacheUtils.put: {key} | cache_id: {id(cache)}')


def get(key):
    """
    从缓存中获取值
    
    参数:
        key: 缓存键
    
    返回:
        缓存值，如果不存在返回 None
    """
    cache = get_cache()
    value = cache.get(key)
    LogUtils.info(f'CacheUtils.get: {key} | cache_id: {id(cache)} | value: {value}')
    return value


def clean():
    """
    清空所有缓存
    """
    _single_cache.clear()
    LogUtils.info('CacheUtils.clean: 缓存已清空')