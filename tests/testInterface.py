#                                                       #
#                 Test GroupUserFolder                  #
#                                                       #
#                                                       #
# (c)2002+ Ingeniweb                                    #


import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


from Log import *

# Load fixture
from Testing import ZopeTestCase
from Interface import Verify
import string


def flattenList(lst):
    """
    flattenList => transform a (deep) sequence into a simple sequence
    """
    ret = []

    if type(lst) not in (type(()), type([])):
        return (lst, )

    for item in lst:
        if type(item) in (type(()), type([]), ):
            ret.extend(flattenList(item))
        else:
            ret.append(item)
    return ret

def flattenInterfaces(lst):
    """
    flattenInterfaces => fetch interfaces and inherited ones
    """
    ret = []
    lst = flattenList(lst)
    for intf in lst:
        bases = intf.getBases()
        ret.extend(flattenInterfaces(bases))
        if not intf in ret:
            ret.append(intf)
    return ret


# Products and global vars
from Products.GroupUserFolder import GroupUserFolder, GRUFUser
##klasses = (        # tell which classes to check
##    GroupUserFolder.GroupUserFolder,
##    GRUFUser.GRUFUser,
##    GRUFUser.GRUFGroup,
##    )


class TestInterface(ZopeTestCase.ZopeTestCase):

    def test01Interfaces(self,):
        """
        Test that interfaces are okay
        """
        # Check interface for each and every class
        ignore = getattr(self, "ignore_interfaces", [])
        for klass in self.klasses:
            intfs = getattr(klass, "__implements__", None)
            self.failUnless(intfs, "'%s' class doesn't implement an interface!" % (klass.__name__, ))

            # Flatten interfaces
            intfs = flattenList(intfs)

            # Check each and everyone
            for intf in intfs:
                if intf in ignore:
                    continue
                self.failUnless(
                    Verify.verifyClass(
                    intf,
                    klass,
                    ),
                    "'%s' class doesn't implement '%s' interface correctly." % (klass.__name__, intf.__name__, ),
                    )


    def test02TestCaseCompletude(self,):
        """
        Check that the test case is complete : each interface entry xxx must be associated
        to a test_xxx method in the test class.
        """
        not_defined = []
        tests = dir(self)
        count = 0
        
        # Check interface for each and every class
        ignore = getattr(self, "ignore_interfaces", [])
        for klass in self.klasses:
            intfs = getattr(klass, "__implements__", None)
            self.failUnless(intfs, "'%s' class doesn't implement an interface!" % (klass.__name__, ))

            # Flatten interfaces
            intfs = flattenInterfaces(intfs)

            # Check each and every interface
            for intf in intfs:
                if intf in ignore:
                    continue
                for name in intf.names():
                    count += 1
                    if not "test_%s" % (name,) in tests:
                        not_defined.append("%s.%s" % (klass.__name__, name))


        # Raise in case some tests are missing
        if not_defined:
            raise RuntimeError, "%d (over %d) MISSING TESTS:\n%s do not have a test associated." % (
                len(not_defined),
                count,
                string.join(not_defined, ", "),
                )
        
        
    def test03ClassSecurityInfo(self):
        """
        This method tests that each and every method has a ClassSecurityInfo() declaration
        XXX This doesn't walk through inheritance :(
        """
        not_defined = []
        count = 0
        
        # Check interface for each and every class
        ignore = getattr(self, "ignore_interfaces", [])
        for klass in self.klasses:
            dict = dir(klass)
            intfs = getattr(klass, "__implements__", None)
            self.failUnless(intfs, "'%s' class doesn't implement an interface!" % (klass.__name__, ))

            # Flatten interfaces
            intfs = flattenInterfaces(intfs)
            
            # Now check the resulting class to see if the mapping was made
            # correctly. Note that this uses carnal knowledge of the internal
            # structures used to store this information!
            # Check each method of every interface
            for intf in intfs:
                if intf in ignore:
                    continue
                for name in intf.names():
                    count += 1
                    if not "%s__roles__" % (name,) in dict:
                        not_defined.append("%s.%s" % (klass.__name__, name))

        # Raise in case some tests are missing
        if not_defined:
            raise RuntimeError, "%d (over %d) MISSING SECURITY DECLARATIONS:\n%s do not have a security declaration associated." % (
                len(not_defined),
                count,
                string.join(not_defined, ", "),
                )
        
