"""ATContentTypes site tests

For tests that needs a plone portal including archetypes and portal transforms

$Id: ATCTSiteTestCase.py,v 1.2 2004/03/16 15:27:10 tiran Exp $
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import time
from common import *
from Products.Archetypes.tests import ArcheSiteTestCase
from Products.ATContentTypes.Extensions.Install import install as installATCT

class ATCTSiteTestCase(ArcheSiteTestCase.ArcheSiteTestCase):
    """ AT Content Types test case based on a plone site with archetypes"""
    def test_dcEdit(self):
        #if not hasattr(self, '_cmf') or not hasattr(self, '_ATCT'):
        #    return
        old = self._cmf
        new = self._ATCT
        dcEdit(old)
        dcEdit(new)
        self.failUnless(old.Title() == new.Title(), 'Title mismatch: %s / %s' \
                        % (old.Title(), new.Title()))
        self.failUnless(old.Description() == new.Description(), 'Description mismatch: %s / %s' \
                        % (old.Description(), new.Description()))
        # XXX more

def setupATCT(app, quiet=0):
    get_transaction().begin()
    _start = time.time()
    if not quiet: ZopeTestCase._print('Installing ATContentTypes ... ')

    uf = app.portal.acl_users
    # login as manager
    user = uf.getUserById('PloneManager').__of__(uf)
    newSecurityManager(None, user)
    # add Archetypes
    installATCT(app.portal)
    
    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
setupATCT(app)
ZopeTestCase.close(app)
