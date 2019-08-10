import motex.common.hextools as hextools
from motex.common.constants import _DEFAULT_METADATA_KEY, _DEFAULT_SECTIONS_KEY
from motex.storage import MotexStorageTracker
from motex.common.base import HelperBase


class MotexSection:
    next_ = None
    prev_ = None
    index_ = None

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if val is not None:
                setattr(self, key, val)

    def __lt__(self, other):
        return hextools.hex_to_int(self.section_virtual_address) < hextools.hex_to_int(other.section_virtual_address)

    def __le__(self, other):
        return hextools.hex_to_int(self.section_virtual_address) <= hextools.hex_to_int(other.section_virtual_address)

    def __gt__(self, other):
        return hextools.hex_to_int(self.section_virtual_address) > hextools.hex_to_int(other.section_virtual_address)

    def __ge__(self, other):
        return hextools.hex_to_int(self.section_virtual_address) >= hextools.hex_to_int(section_virtual_address.offset)

    def __eq__(self, other):
        return hextools.hex_to_int(self.section_virtual_address) == hextools.hex_to_int(other.section_virtual_address)

    def __str__(self):
        return "%s: <MotexSection> (%s)" % (self.section_virtual_address, self.section_name)

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
                'section_name': self.section_name,
                'section_type': self.section_type,
                'section_offset': self.section_offset,
                'section_virtual_address': self.section_virtual_address,
                'section_size': self.section_size,
                'section_entry_size': self.section_entry_size,
                'section_entropy': self.section_entropy,
                'section_segments': self.section_segments,}


class MotexSectionStorageHelper(MotexStorageTracker):
    first = None
    count = 0
    prev_ = None

    @classmethod
    def prepare(cls, storage):
        storage.cleanup(_DEFAULT_SECTIONS_KEY)

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
            storage.store(_DEFAULT_SECTIONS_KEY, cls.prev_.index_, cls.prev_.to_dict())

        cls.prev_ = current
        cls.count = cls.count + 1

    @classmethod
    def complete(cls, storage=None):
        if cls.prev_ is None:
            return

        cls.prev_.next_ = None
        field = cls.prev_.index_

        if storage is not None and cls.prev_ is not None:
            storage.store(_DEFAULT_SECTIONS_KEY, field, cls.prev_.to_dict())

            field = 'sections_first'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.first)

            field = 'sections_last'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.prev_.get_id())

            field = 'sections_count'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.count)


class MotexSectionHelper(HelperBase):
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
        field = 'symbols_first'
        first = self._storage.load(_DEFAULT_METADATA_KEY, field)
        if first is None:
            return None

        data = self._storage.load(_DEFAULT_SECTIONS_KEY, first)
        if data != None:
            return MotexSection(**data)
        return None

    def _get_last(self):
        field = 'symbols_last'
        first = self._storage.load(_DEFAULT_METADATA_KEY, field)
        if first is None:
            return None

        data = self._storage.load(_DEFAULT_SECTIONS_KEY, first)
        if data != None:
            return MotexSection(**data)
        return None

    def _get_count(self):
        field = 'symbols_count'
        return self._storage.load(_DEFAULT_METADATA_KEY, field)

    def all(self):
        return self.__iter__()

    def __iter__(self):
        '''
        >>> for ins in MotexSectionHelper(storage).all():
        ...  print str(ins)
        ...
        0x01
        0x02
        0x03
        0x04
        '''
        curr = self._first
        while curr.get_id() != None:
            data = self._storage.load(_DEFAULT_SECTIONS_KEY, curr.get_id()) or dict()
            curr = MotexSection(**data)

            yield curr

            data = dict()
            if curr.get_next_id() is not None:
                data = self._storage.load(_DEFAULT_SECTIONS_KEY, curr.get_next_id())

            next_curr = MotexSection(**data)
            curr = next_curr

    def reverse(self):
        '''
        >>> for ins in MotexSectionHelper(storage).reverse():
        ...  print str(ins)
        ...
        0x04 <MotexSection> sec
        0x03 <MotexSection> sec
        0x02 <MotexSection> sec
        0x01 <MotexSection> sec
        '''
        curr = self._last
        while curr.get_id() != None:
            data = self._storage.load(_DEFAULT_SECTIONS_KEY, curr.get_id()) or dict()
            curr = MotexSection(**data)

            yield curr

            data = dict()
            if curr.get_prev_id() is not None:
                data = self._storage.load(_DEFAULT_SECTIONS_KEY, curr.get_prev_id())

            next_curr = MotexSection(**data)
            curr = next_curr

    def get(self, index):
        '''
        >>> ins = MotexSectionHelper(storage).get(addr):
        ... print str(ins)
        ...
        0x04 <MotexSection> sec
        '''
        if not isinstance(index, str):
            raise Exception("index must be string")

        data = self._storage.load(_DEFAULT_SECTIONS_KEY, index) or dict()
        return MotexSection(**data)
