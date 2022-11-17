import threading

lock = threading.RLock()
_instance = {}


# 单例模式
def singleton(cls):
    # 创建字典用来保存类的实例对象
    global _instance

    def _singleton(*args, **kwargs):
        # 先判断这个类有没有对象
        if cls not in _instance:
            with lock:
                if cls not in _instance:
                    _instance[cls] = cls(*args, **kwargs)
                    pass
        # 将实例对象返回
        return _instance[cls]

    return _singleton