from motex.storage.backend import StorageBackend
from motex.storage.formatter import StorageFormatter


class MotexStorage:
    def __init__(self, storage_backend, storage_format, **kwargs):
        self.storage_format = storage_format or 'json'

        if not isinstance(storage_format, str):
            raise Exception("storage formatter must be string")

        if not isinstance(storage_backend, str):
            raise Exception("storage formatter must be string")

        self.backend = StorageBackend.get_backend(storage_backend, **kwargs)
        self.formatter = StorageFormatter.get_formatter(storage_format)

    def store(self, key, field, value):
        return self.backend.store(key, field, self.formatter.serialize(value))

    def load(self, key, field):
        data = self.backend.load(key, field)
        if data is None:
            return None
        else:
            return self.formatter.deserialize(self.backend.load(key, field))

    def delete(self, key, field):
        return self.backend.delete(key, field)

    def cleanup(self, key):
        return self.backend.cleanup(key)


class MotexStorageTracker:
    @classmethod
    def prev_is_nil(cls):
        if isinstance(cls.prev_, str):
            return True if cls.prev_ == 'nil' else False
        else:
            return False

    @classmethod
    def next_is_nil(cls):
        if isinstance(cls.next_, str):
            return True if cls.next_ == 'nil' else False
        else:
            return False
