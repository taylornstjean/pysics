import weakref
import itertools
from collections import defaultdict


_id = itertools.count()


class KeepRefs:

    __refs__ = defaultdict(list)

    def __init__(self) -> None:
        self.__refs__[self.__class__].append(self)
        self._id = next(_id)

    @classmethod
    def instances(cls):
        for ref in cls.__refs__[cls]:
            if ref is not None:
                yield ref
