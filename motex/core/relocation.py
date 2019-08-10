import motex.common.hextools as hextools
from motex.common.constants import _DEFAULT_METADATA_KEY, _DEFAULT_RELOCATIONS_KEY
from motex.storage import MotexStorageTracker
from motex.common.base import HelperBase


class MotexRelocation:
    next_ = None
    prev_ = None
    index_ = None

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if val is not None:
                setattr(self, key, val)

    def __lt__(self, other):
        return hextools.hex_to_int(self.relocation_address) < hextools.hex_to_int(other.relocation_address)

    def __le__(self, other):
        return hextools.hex_to_int(self.relocation_address) <= hextools.hex_to_int(other.relocation_address)

    def __gt__(self, other):
        return hextools.hex_to_int(self.relocation_address) > hextools.hex_to_int(other.relocation_address)

    def __ge__(self, other):
        return hextools.hex_to_int(self.relocation_address) >= hextools.hex_to_int(other.relocation_address)

    def __eq__(self, other):
        return hextools.hex_to_int(self.relocation_address) == hextools.hex_to_int(other.relocation_address)

    def __str__(self):
        return "%s: <MotexRelocation> (%s)" % (self.relocation_symbol_name, self.relocation_address)

    def get_id(self):
        return self.index_

    def get_next_id(self):
        return self.next_

    def get_prev_id(self):
        return self.prev_

    def to_dict(self):
        return {'prev_': self.prev_,
                'next_': self.next_,
                'index_': self.index_,
                'relocation_address': self.relocation_address,
                'relocation_type': self.relocation_type,
                'relocation_symbol_value': self.relocation_symbol_value,
                'relocation_symbol_name': self.relocation_symbol_name,
                'relocation_computed_plt_address': self.relocation_computed_plt_address,}


class MotexRelocationStorageHelper(MotexStorageTracker):
    first = None
    count = 0
    prev_ = None

    @classmethod
    def prepare(cls, storage):
        storage.cleanup(_DEFAULT_RELOCATIONS_KEY)

    @classmethod
    def save(cls, index=0, current=None, prev=None, storage=None):
        field = str(index)
        current.index_ = field

        if cls.first is None:
            cls.first = field

        if cls.prev_ is not None:
            cls.prev_.next_ = field
            current.prev_ = cls.prev_.index_

        if storage is not None and cls.prev_ is not None:
            storage.store(_DEFAULT_RELOCATIONS_KEY, cls.prev_.index_, cls.prev_.to_dict())

        cls.prev_ = current
        cls.count = cls.count + 1

    @classmethod
    def complete(cls, storage=None):
        if cls.prev_ is None:
            return

        cls.prev_.next_ = None
        field = cls.prev_.index_

        if storage is not None and cls.prev_ is not None:
            storage.store(_DEFAULT_RELOCATIONS_KEY, field, cls.prev_.to_dict())

            field = 'relocations_first'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.first)

            field = 'relocations_last'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.prev_.get_id())

            field = 'relocations_count'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.count)


class MotexRelocationHelper(HelperBase):
    def __init__(self, storage):
        self._storage = storage
        self._first = self._get_first()
        self._last = self._get_last()
        self._count = self._get_count()

    @property
    def count(self):
        return self._count
    
    @property
    def first(self):
        return self._first

    def _get_first(self):
        field = 'relocations_first'
        first = self._storage.load(_DEFAULT_METADATA_KEY, field)
        if first is None:
            return None

        data = self._storage.load(_DEFAULT_RELOCATIONS_KEY, first)
        if data != None:
            return MotexRelocation(**data)
        return None

    def _get_last(self):
        field = 'relocations_last'
        first = self._storage.load(_DEFAULT_METADATA_KEY, field)
        if first is None:
            return None

        data = self._storage.load(_DEFAULT_RELOCATIONS_KEY, first)
        if data != None:
            return MotexRelocation(**data)
        return None

    def _get_count(self):
        field = 'relocations_count'
        return self._storage.load(_DEFAULT_METADATA_KEY, field)

    def all(self):
        return self.__iter__()

    def __iter__(self):
        '''
        >>> for ins in MotexRelocationHelper(storage).all():
        ...  print str(ins)
        ...
        0x01
        0x02
        0x03
        0x04
        '''
        curr = self._first
        while curr.get_id() != None:
            data = self._storage.load(_DEFAULT_RELOCATIONS_KEY, curr.get_id()) or dict()
            curr = MotexRelocation(**data)

            yield curr

            data = dict()
            if curr.get_next_id() is not None:
                data = self._storage.load(_DEFAULT_RELOCATIONS_KEY, curr.get_next_id())

            next_curr = MotexRelocation(**data)
            curr = next_curr

    def reverse(self):
        '''
        >>> for ins in MotexRelocationHelper(storage).reverse():
        ...  print str(ins)
        ...
        0x04 <MotexRelocation> reloc
        0x03 <MotexRelocation> reloc
        0x02 <MotexRelocation> reloc
        0x01 <MotexRelocation> reloc
        '''
        curr = self._last
        while curr.get_id() != None:
            data = self._storage.load(_DEFAULT_RELOCATIONS_KEY, curr.get_id()) or dict()
            curr = MotexRelocation(**data)

            yield curr

            data = dict()
            if curr.get_prev_id() is not None:
                data = self._storage.load(_DEFAULT_RELOCATIONS_KEY, curr.get_prev_id())

            next_curr = MotexRelocation(**data)
            curr = next_curr

    def get(self, index):
        '''
        >>> ins = MotexRelocationHelper(storage).get(addr):
        ... print str(ins)
        ...
        0x04 <MotexRelocation> reloc
        '''
        if not isinstance(index, str):
            raise Exception("index must be string")

        data = self._storage.load(_DEFAULT_RELOCATIONS_KEY, index) or dict()
        return MotexRelocation(**data)
