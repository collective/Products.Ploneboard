"""
Stubs for the tests.

$Id: stubs.py,v 1.1 2004/02/08 16:30:37 k_vertigo Exp $
"""
from Acquisition import Implicit

class Stub:
    def __init__(self, **kw):
        self.__dict__.update(kw)

class SecurityPolicyStub(Stub):
    def validate(self, *args, **kw):
        return 1
    def checkPermission(self, **kw):
        return 1

class AnonymousUserStub(Implicit):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def getId(self):
        return 'unit_tester'
    getUserName = getId

    def has_permission(self, **kw):
        return 1

    def allowed( self, object, object_roles=None ):
        return 1

    def getRoles(self):
        return ('Anonymous',)
