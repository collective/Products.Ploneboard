import OFS

class Key(OFS.SimpleItem.SimpleItem):
    key = None


    def __init__(self, key):
        self.key = key


    def __cmp__(self, k):
        keylen = len(self.key)
        for i in range(0, keylen-1):
            if self.key[i] != k.key[i]:
                return self._compare(self.key[i], k.key[i])
        return self._compare(self.key[keylen-1], k.key[keylen-1])


    def _compare(self, k1, k2):
        # make None end up last
        if k1 == None:
            if k2 == None:
                return 0
            return 1
        if k2 == None:
            return -1
        return cmp(k1, k2)

    def getKey(self):
        return self.key

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, k):
        return self.key == k.key
