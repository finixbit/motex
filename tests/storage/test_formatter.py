from __future__ import absolute_import, print_function

import pytest

from motex.storage.formatter import (
    StorageFormatter,
    StorageJsonFormatter,
    StorageMsgpackFormatter,
)


class TestStorageFormatter:
    def test_storage_formatter_len(self):
        test_data = [1, 2, 3]
        assert len(StorageFormatter.formatters.items()) == 2

    def test_storage_formatter_keys(self):
        assert StorageFormatter.formatters.get('json') is not None
        assert StorageFormatter.formatters.get('invalid_format_key') is None


class TestStorageJsonFormatter:
    def test_storage_json_formatter_name(self):
        assert StorageJsonFormatter.__format_name__ == 'json'

    def test_storage_json_formatter_serialize_valid_argument(self):
        test_data = [1, 2, 3]
        assert StorageJsonFormatter.serialize(test_data) == '[1, 2, 3]'

    def test_storage_json_formatter_serialize_invalid_argument(self):
        with pytest.raises(ValueError) as e:
            assert StorageJsonFormatter.serialize(None)

    def test_storage_json_formatter_deserialize_valid_argument(self):
        test_data = '[1, 2, 3]'
        assert StorageJsonFormatter.deserialize(test_data) == [1, 2, 3]

    def test_storage_json_formatter_deserialize_invalid_argument(self):
        with pytest.raises(ValueError) as e:
            assert StorageJsonFormatter.deserialize(None)


class TestStorageMsgpackFormatter:
    def test_storage_msgpack_formatter_name(self):
        assert StorageMsgpackFormatter.__format_name__ == 'msgpack'

    def test_storage_msgpack_formatter_serialize_valid_argument(self):
        test_data = [1, 2, 3]
        assert StorageMsgpackFormatter.serialize(test_data) == b'\x93\x01\x02\x03'

    def test_storage_msgpack_formatter_serialize_invalid_argument(self):
        with pytest.raises(ValueError) as e:
            assert StorageMsgpackFormatter.serialize(None)
