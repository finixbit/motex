import motex.common.hextools as hextools
from motex.common.constants import _DEFAULT_METADATA_KEY, _DEFAULT_FUNCTIONS_KEY
from motex.storage import MotexStorageTracker
from motex.common.base import HelperBase


class MotexFunction:
    next_ = None
    prev_ = None
    index_ = None
    address = '0x0'

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __lt__(self, other):
        return hextools.hex_to_int(self.address) < hextools.hex_to_int(other.address)

    def __le__(self, other):
        return hextools.hex_to_int(self.address) <= hextools.hex_to_int(other.address)

    def __gt__(self, other):
        return hextools.hex_to_int(self.address) > hextools.hex_to_int(other.address)

    def __ge__(self, other):
        return hextools.hex_to_int(self.address) >= hextools.hex_to_int(other.address)

    def __eq__(self, other):
        return hextools.hex_to_int(self.address) == hextools.hex_to_int(other.address)

    def __str__(self):
        return "%s: <MotexFunction> (%s)" % (self.address, self.name)

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
                'address': self.address,
                'name': self.name,
                'basicblock_leaders': self.basicblock_leaders,
                'function_edges': self.function_edges,
                'callsites_list': self.callsites_list,
                'basicblock_edges': self.basicblock_edges,
                'instructions_list': self.instructions_list}


class MotexFunctionStorageHelper(MotexStorageTracker):
    first = None
    count = 0
    prev_ = None

    @classmethod
    def prepare(cls, storage):
        storage.cleanup(_DEFAULT_FUNCTIONS_KEY)

    @classmethod
    def save(cls, index=None, current=None, prev=None, storage=None):
        field = index
        current.index_ = field

        if cls.first is None:
            cls.first = field

        if cls.prev_ is not None:
            cls.prev_.next_ = field
            current.prev_ = cls.prev_.index_

        if storage is not None and cls.prev_ is not None:
            storage.store(_DEFAULT_FUNCTIONS_KEY, cls.prev_.index_, cls.prev_.to_dict())

        cls.prev_ = current
        cls.count = cls.count + 1

    @classmethod
    def complete(cls, storage=None):
        if cls.prev_ is None:
            return

        cls.prev_.next_ = None
        field = cls.prev_.index_

        if storage is not None and cls.prev_ is not None:
            storage.store(_DEFAULT_FUNCTIONS_KEY, field, cls.prev_.to_dict())

            field = 'functions_first'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.first)

            field = 'functions_last'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.prev_.get_id())

            field = 'functions_count'
            storage.store(_DEFAULT_METADATA_KEY, field, cls.count)


class MotexFunctionHelper(HelperBase):
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
        field = 'functions_first'
        first = self._storage.load(_DEFAULT_METADATA_KEY, field)
        if first is None:
            return None

        data = self._storage.load(_DEFAULT_FUNCTIONS_KEY, first)
        if data != None:
            return MotexFunction(**data)
        return None

    def _get_last(self):
        field = 'functions_last'
        first = self._storage.load(_DEFAULT_METADATA_KEY, field)
        if first is None:
            return None

        data = self._storage.load(_DEFAULT_FUNCTIONS_KEY, first)
        if data != None:
            return MotexFunction(**data)
        return None

    def _get_count(self):
        field = 'functions_count'
        return self._storage.load(_DEFAULT_METADATA_KEY, field)

    def all(self):
        return self.__iter__()

    def __iter__(self):
        '''
        >>> for ins in MotexFunctionHelper(storage).all():
        ...  print str(ins)
        ...
        0x01
        0x02
        0x03
        0x04
        '''
        curr = self._first
        while curr.get_id() != None:
            data = self._storage.load(_DEFAULT_FUNCTIONS_KEY, curr.get_id()) or dict()
            curr = MotexFunction(**data)

            yield curr

            data = dict()
            if curr.get_next_id() is not None:
                data = self._storage.load(_DEFAULT_FUNCTIONS_KEY, curr.get_next_id())

            next_curr = MotexFunction(**data)
            curr = next_curr

    def reverse(self):
        '''
        >>> for ins in MotexFunctionHelper(storage).reverse():
        ...  print str(ins)
        ...
        0x04 <MotexFunction> function_name
        0x03 <MotexFunction> function_name
        0x02 <MotexFunction> function_name
        0x01 <MotexFunction> function_name
        '''
        curr = self._last
        while curr.get_id() != None:
            data = self._storage.load(_DEFAULT_FUNCTIONS_KEY, curr.get_id()) or dict()
            curr = MotexFunction(**data)

            yield curr

            data = dict()
            if curr.get_prev_id() is not None:
                data = self._storage.load(_DEFAULT_FUNCTIONS_KEY, curr.get_prev_id())

            next_curr = MotexFunction(**data)
            curr = next_curr

    def get(self, index):
        '''
        >>> ins = MotexFunctionHelper(storage).get(addr):
        ... print str(ins)
        ...
        0x04 <MotexFunction> function_name
        '''
        if not isinstance(index, str):
            raise Exception("index must be string")

        data = self._storage.load(_DEFAULT_FUNCTIONS_KEY, index) or dict()
        return MotexFunction(**data)
