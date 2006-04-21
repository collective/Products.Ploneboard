import Globals, sys

from DateTime import DateTime
from Persistence import Persistent

from BTrees.Length import Length
from BTrees.IIBTree import IIBTree

class PloneboardIndex(Persistent):
    """A class for containing the date indexes and handling length (map to __len__)"""
    _count = None         # A BTrees.Length
    _dates = None         # IIBTree: { date as int -> id (message and conversation ID always int) }
    _reverse_dates = None # IIBTree: { id -> date as int }

    def __init__(self):
        self._count = Length()
        self._dates = IIBTree()
        self._reverse_dates = IIBTree()

    def __len__(self):
        return self._count()
    
    def has_key(self, key):
        """Pass through to _dates"""
        return self._dates.has_key(key)

    def get(self, key, default=None):
        """Pass through to _dates"""
        return self._dates.get(key, default)

    def values(self, min=None, max=None):
        """Pass through to _dates"""
        return self._dates.values(min, max)

    def keys(self, min=None, max=None):
        """Pass through to _dates"""
        return self._dates.keys(min, max)
    
    def items(self, min=None, max=None):
        """Pass through to _dates"""
        return self._dates.items(min, max)
    
    def maxKey(self, key=None):
        """Pass through to _dates"""
        return self._dates.maxKey()
        
    def minKey(self, key=None):
        """Pass through to _dates"""
        return self._dates.minKey()

    def _calculateInternalDateKey(self, date):
        # Date key - use max int minus seconds since epoch as key in date index
        return sys.maxint - int(date)

    def setDateKey(self, id, date=DateTime()):
        """
        Update the _dates and _reverse_dates indexes, recent entries last
        return 1 if added, 0 if modified and -1 if an exception occured
        """
        retvalue = -1
        try:
            # ID is supposed to be int
            id = int(id)

            # Calculate the date key
            datekey = self._calculateInternalDateKey(date)

            dates = self._dates
            reverse = self._reverse_dates

            # Check if there already exists an entry for the id
            oldkey = reverse.get(id, None)
            if oldkey:
                del dates[oldkey]
                retvalue = 0
            else:
                # Add to object counter
                self._count.change(1)
                retvalue = 1
                
            # Make sure datekeys don't collide
            while dates.has_key(datekey):
                datekey -= 1
            dates[datekey] = id
            reverse[id] = datekey

        except ValueError:
            # Only objects with int id in the index
            retvalue = -1

        return retvalue

    def delDateKey(self, id):
        """
        Delete from dates index
        return 1 if deleted, 0 if key did not exist, and -1 otherwise
        """
        retvalue = 0
        try:
            id = int(id)
            datekey = self._reverse_dates.get(id, None)
            if datekey is not None:
                del self._reverse_dates[id]
                del self._dates[datekey]
                self._count.change(-1)
                retvalue = 1
        except ValueError:
            # Only objects with int id in the index
            retvalue = -1

        return retvalue

    __setitem__ = setDateKey
    __delitem__ = delDateKey


class ForumIndex(PloneboardIndex):
    """
    A class for containing the date indexes and handling length (map to __len__)
    """
    def _calculateInternalDateKey(self, date):
        # Date key - use max int minus seconds since epoch as key in date index
        return sys.maxint - int(date)
