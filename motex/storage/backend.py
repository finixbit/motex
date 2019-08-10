from __future__ import absolute_import, print_function

import abc
from vedis import Vedis


class StorageBackendBase(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractproperty
    def __backend_name__(cls):
        raise NotImplementedError()

    @abc.abstractmethod
    def __init__(self, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def store(self, key, field, value):
        raise NotImplementedError()

    @abc.abstractmethod
    def load(self, key, field):
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, key, field):
        raise NotImplementedError()


class StorageBackend(StorageBackendBase):
    backends = dict()

    def __init_subclass__(cls, *args, **kwargs):
        cls.backends[cls.__backend_name__] = cls
        super().__init_subclass__(*args, **kwargs)

    @classmethod
    def get_backend(cls, backend_name, **kwargs):
        backend = cls.backends.get(backend_name)
        if backend is None:
            raise Exception(f"{backend_name} Backend not supported")
        return backend(**kwargs)


class StorageBackendVedis(StorageBackend):
    __backend_name__ = 'vedis'

    def __init__(self, **kwargs):
        if kwargs is None or kwargs.get('database_path') is None:
            raise Exception("Vedis backend requires path argument")

        self.database_path = kwargs.get('database_path')
        self.db = Vedis(self.database_path)

    def store(self, key, field, value):
        if not all(map(lambda x: isinstance(x, str), [key, field, value])):
            raise Exception('key, field, value must be string')

        _hash = self.db.Hash(key)
        _hash[field] = value
        return True

    def load(self, key, field):
        if not all(map(lambda x: isinstance(x, str), [key, field])):
            raise Exception('key, field must be string')

        _hash = self.db.Hash(key)
        return _hash[field]

    def delete(self, key, field):
        if not all(map(lambda x: isinstance(x, str), [key, field])):
            raise Exception('key, field must be string')

        _hash = self.db.Hash(key)
        del _hash[field]
        return True

    def cleanup(self, key):
        if not isinstance(key, str):
            raise Exception('key must be string')
            
        _hash = self.db.Hash(key)
        try:
            for _hkey in _hash:
                del _hash[_hkey]
        except:
            pass

class StorageBackendRedis(StorageBackend):
    __backend_name__ = 'redis'
    pass
