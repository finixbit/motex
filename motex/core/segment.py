import motex.common.hextools as hextools
from motex.common.constants import _DEFAULT_METADATA_KEY, _DEFAULT_SEGMENTS_KEY
from motex.storage import MotexStorageTracker
from motex.common.base import HelperBase


class MotexSegment:
    next_ = None
    prev_ = None
    index_ = None

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if val is not None:
                setattr(self, key, val)

    def __lt__(self, other):
        return hextools.hex_to_int(self.segment_offset) < hextools.hex_to_int(other.segment_offset)

    def __le__(self, other):
        return hextools.hex_to_int(self.segment_offset) <= hextools.hex_to_int(other.segment_offset)

    def __gt__(self, other):
        return hextools.hex_to_int(self.segment_offset) > hextools.hex_to_int(other.segment_offset)

    def __ge__(self, other):
        return hextools.hex_to_int(self.segment_offset) >= hextools.hex_to_int(other.segment_offset)

    def __eq__(self, other):
        return hextools.hex_to_int(self.segment_offset) == hextools.hex_to_int(other.segment_offset)

    def __str__(self):
        if self.segment_offset == None:
            return None
        else:
            return "%s: <MotexSegment> (%s)" % (self.segment_offset, self.segment_type)

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
                'segment_type': self.segment_type,
                'segment_offset': self.segment_offset,
                'segment_virtual_address': self.segment_virtual_address,
                'segment_virtual_size': self.segment_virtual_size,
                'segment_physical_address': self.segment_physical_address,
                'segment_physical_size': self.segment_physical_size,
                'segment_flags': self.segment_flags,
                'segment_sections': self.segment_sections,
                'segment_section_addrs': self.segment_section_addrs,}


class MotexSegmentStorageHelper(MotexStorageTracker):
    first = None
    count = 0
    prev_ = None

    @classmethod
    def prepare(cls, storage):
        storage.cleanup(_DEFAULT_SEGMENTS_KEY)

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
            storage.store(_DEFAULT_SEGMENTS_KEY, cls.prev_.index_, cls.prev_.to_dict())

        cls.prev_ = current
        cls.count = cls.count + 1

    @classmethod
    def complete(cls, storage=None):
        if cls.prev_ is None:
            return

        cls.prev_.next_ = None
        field = cls.prev_.index_

        if storage is not None and cls.prev_ is not None:
            storage.store(_DEFAULT_SEGMENTS_KEY, field, cls.prev_.to_dict())

            field = 'segments_first'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.first)

            field = 'segments_last'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.prev_.get_id())

            field = 'segments_count'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.count)


class MotexSegmentHelper(HelperBase):
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
        field = 'segments_first'
        first = self._storage.load(_DEFAULT_METADATA_KEY, field)
        if first is None:
            return None

        data = self._storage.load(_DEFAULT_SEGMENTS_KEY, first)
        if data != None:
            return MotexSegment(**data)
        return None

    def _get_last(self):
        field = 'segments_last'
        first = self._storage.load(_DEFAULT_METADATA_KEY, field)
        if first is None:
            return None

        data = self._storage.load(_DEFAULT_SEGMENTS_KEY, first)
        if data != None:
            return MotexSegment(**data)
        return None

    def _get_count(self):
        field = 'segments_count'
        return self._storage.load(_DEFAULT_METADATA_KEY, field)

    def all(self):
        return self.__iter__()

    def __iter__(self):
        '''
        >>> for ins in MotexSegmentHelper(storage).all():
        ...  print str(ins)
        ...
        0x01
        0x02
        0x03
        0x04
        '''
        curr = self._first
        while curr.get_id() != None:
            data = self._storage.load(_DEFAULT_SEGMENTS_KEY, curr.get_id()) or dict()
            curr = MotexSegment(**data)

            yield curr

            data = dict()
            if curr.get_next_id() is not None:
                data = self._storage.load(_DEFAULT_SEGMENTS_KEY, curr.get_next_id())

            next_curr = MotexSegment(**data)
            curr = next_curr

    def reverse(self):
        '''
        >>> for ins in MotexSegmentHelper(storage).reverse():
        ...  print str(ins)
        ...
        0x04 <MotexSegment> seg
        0x03 <MotexSegment> seg
        0x02 <MotexSegment> seg
        0x01 <MotexSegment> seg
        '''
        curr = self._last
        while curr.get_id() != None:
            data = self._storage.load(_DEFAULT_SEGMENTS_KEY, curr.get_id()) or dict()
            curr = MotexSegment(**data)

            yield curr

            data = dict()
            if curr.get_prev_id() is not None:
                data = self._storage.load(_DEFAULT_SEGMENTS_KEY, curr.get_prev_id())

            next_curr = MotexSegment(**data)
            curr = next_curr

    def get(self, index):
        '''
        >>> ins = MotexSegmentHelper(storage).get(addr):
        ... print str(ins)
        ...
        0x04 <MotexSegment> seg
        '''
        if not isinstance(index, str):
            raise Exception("index must be string")

        data = self._storage.load(_DEFAULT_SEGMENTS_KEY, index) or dict()
        return MotexSegment(**data)
