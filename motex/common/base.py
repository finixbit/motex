from __future__ import absolute_import, print_function

import abc


class HelperMeta(metaclass=abc.ABCMeta):

    def all(self):
        raise NotImplementedError()

    def get(self, index):
        raise NotImplementedError()


class HelperBase(HelperMeta):
    pass
