from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Products.Ploneboard.Extensions.Install import install as installPloneboard
from Products.Ploneboard.Ploneboard import Ploneboard
from Products.Ploneboard.PloneboardForum import PloneboardForum
from Products.CMFPlone.tests import PloneTestCase
import time
import utils

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Ploneboard')


class PloneboardTestCase(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.refreshSkinData()
        self.loginPortalOwner()
        utils.disableScriptValidators(self.portal)
                
        className = self.__class__.__name__
        if className == 'TestPloneboardForum':
            self.portal._setObject('board', Ploneboard('board'))
            self.catalog = self.portal.board.getInternalCatalog()
        elif className == 'TestPloneboardConversation':
            self.portal._setObject('board', Ploneboard('board'))
            self.portal.board._setObject('forum', PloneboardForum('forum'))
            self.catalog = self.portal.board.getInternalCatalog()
        elif className == 'TestPloneboardMessage':
            self.portal._setObject('board', Ploneboard('board'))
            self.portal.board._setObject('forum', PloneboardForum('forum'))
            self.conv = self.portal.board.forum.addConversation('conv1', 'conv1 body')
            self.catalog = self.portal.board.getInternalCatalog()
        
        self.logout()
        
def setupPloneboard(app, quiet=0):
    get_transaction().begin()
    _start = time.time()
    if not quiet: ZopeTestCase._print('Adding Ploneboard ... ')

    uf = app.portal.acl_users
    # setup
    uf._doAddUser('PloneMember', '', ['Members'], [])
    uf._doAddUser('PloneManager', '', ['Manager'], [])
    # login as manager
    user = uf.getUserById('PloneManager').__of__(uf)
    newSecurityManager(None, user)
    
    # add Ploneboard
    installPloneboard(app.portal)
    
    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
setupPloneboard(app)
ZopeTestCase.close(app)