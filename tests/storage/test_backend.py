from __future__ import absolute_import, print_function

import pytest

from motex.storage.backend import (
    StorageBackend,
    StorageBackendVedis,
    StorageBackendRedis,
)


class TestStorageBackend:
    def test_storage_backend_len(self):
        test_data = [1, 2, 3]
        assert len(StorageBackend.backends.items()) == 2

    def test_storage_backend_keys(self):
        assert StorageBackend.backends.get('vedis') is not None
        assert StorageBackend.backends.get('invalid_backend_key') is None


class TestStorageBackendVedis:
    def test_backend_vedis_name(self):
        assert StorageBackendVedis.__backend_name__ == 'vedis'

    def test_backend_vedis_init_valid_arguments(self):
        assert StorageBackendVedis(database_path=':mem:')

    def test_backend_vedis_init_invalid_arguments(self):
        with pytest.raises(Exception) as e:
            assert StorageBackendVedis()
            assert StorageBackendVedis(database_path=None)
        assert str(e.value) == f"Vedis backend requires path argument"

    def test_backend_vedis_load(self):
        pass

    def test_backend_vedis_store(self):
        pass

    def test_backend_vedis_delete(self):
        pass


class TestStorageBackendRedis:
    def test_backend_redis_name(self):
        assert StorageBackendRedis.__backend_name__ == 'redis'
