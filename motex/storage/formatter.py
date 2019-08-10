from __future__ import absolute_import, print_function

import abc
import simplejson as json
import msgpack


class StorageFormatterBase(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractproperty
    def __format_name__(cls):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def serialize(cls, data):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, data):
        raise NotImplementedError()


class StorageFormatter(StorageFormatterBase):
    formatters = dict()

    def __init_subclass__(cls, *args, **kwargs):
        cls.formatters[cls.__format_name__] = cls
        super().__init_subclass__(*args, **kwargs)

    @classmethod
    def get_formatter(cls, format_name):
        formatter = cls.formatters.get(format_name)
        if formatter is None:
            raise Exception(f"{format_name} Backend not supported")
        return formatter


class StorageJsonFormatter(StorageFormatter):
    __format_name__ = 'json'

    @classmethod
    def serialize(cls, data):
        if data is None:
            raise ValueError("data must cannot be none")

        serialized_data = json.dumps(data)
        return serialized_data

    @classmethod
    def deserialize(cls, data=None):
        if not isinstance(data, (str, bytes)):
            raise ValueError("data must be string/bytes")

        deserialized_data = json.loads(data)
        return deserialized_data


class StorageMsgpackFormatter(StorageFormatter):
    __format_name__ = 'msgpack'

    @classmethod
    def serialize(cls, data):
        if data is None:
            raise ValueError("data must cannot be none")

        serialized_data = msgpack.packb(data)
        return serialized_data

    @classmethod
    def deserialize(cls, data):
        if not isinstance(data, str):
            raise Exception("data must be string")

        deserialized_data = msgpack.unpackb(data.encode("utf-8"), allow_invalid_utf8=True)
        return deserialized_data
