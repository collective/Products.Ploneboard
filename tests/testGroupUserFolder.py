#                                                       #
#                 Test GroupUserFolder                  #
#                                                       #
#                                                       #
# (c)2002 Ingeniweb                                     #

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))



# Load fixture
from Testing import ZopeTestCase

# Permissions / security
from AccessControl.Permissions import access_contents_information, view, add_documents_images_and_files, change_images_and_files, view_management_screens
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager, getSecurityManager
from AccessControl import Unauthorized
from Products.CMFCore.CMFCorePermissions import *
from AccessControl.User import UnrestrictedUser

import urllib

# Create the error_log object
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.close(app)

# Start the web server
host, port = ZopeTestCase.utils.startZServer(4)
base = 'http://%s:%d/%s' %(host, port, ZopeTestCase._folder_name)

    
# Get global vars
from Products.GroupUserFolder.global_symbols import *


# Install our product
ZopeTestCase.installProduct('GroupUserFolder')


# Set log options if Log module is available
# This is done to set LOG_PROCESSORs to file logs instead of Zope logs
try:
    import Log

    Log.LOG_LEVEL = Log.LOG_DEBUG

    Log.LOG_PROCESSOR = {
        Log.LOG_NONE: Log.logFile,
        Log.LOG_CRITICAL: Log.logFile,
        Log.LOG_ERROR: Log.logFile,
        Log.LOG_WARNING: Log.logFile,
        Log.LOG_NOTICE: Log.logFile,
        Log.LOG_DEBUG: Log.logFile,
        }

    from Log import *
    Log(LOG_NOTICE, "Starting %s at %d debug level" % (os.path.dirname(__file__), LOG_LEVEL, ))

except:
    print "Log module not available"
    LOG_DEBUG = None
    LOG_NOTICE = None
    LOG_WARNING = None
    LOG_ERROR = None
    LOG_CRITICAL = None
    def Log(*args, **kw):
        pass
    raise



class ManagementOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm): 
        return ('manager', 'secret')
        
class UnauthorizedOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm): 
        raise Unauthorized, 'The URLopener was asked for authentication'


class TestGroupUserFolder(ZopeTestCase.ZopeTestCase):


    def login(self, user = None):
        "user must be an acl_user's user"
        self.logout()                   # Is this necessary ? Well, at least, it's clean.
        if not user:
            user = self._user
        newSecurityManager(None, user)


    
    def afterSetUp(self,):
        """
        afterSetUp(self) => This method is called to create Folder with a GRUF inside.

        It creates:
          * 3 roles, r1, r2 and r3
          * 3 groups: g1, g2, g3
          * n users as follows (roles are between parenthesis)

                      !   g1    ! g2(r1)     ! g3(r2)     ! g4(r2,r3)  !  Resulting roles !
          ------------!---------!------------!------------!------------!------------------!
          u1          !         !            !            !            !   => (no role)   !
          u2          !   X     !            !            !            !   => (no role)   !
          u3          !   X     !      X     !            !            !   => r1          !
          u4          !   X     !      X     !      X     !            !   => r1,r2       !
          u5(r1)      !         !      X     !      X     !            !   => r1,r2       !
          u6(r1)      !         !            !      X     !            !   => r1,r2       !
          u7(r1)      !         !            !            !     X      !   => r1,r2,r3    !
          ---------------------------------------------------------------------------------

        It also creates a 'lr' folder in which g1 group and u3 and u6 are granted r3 role.

        """
        # Replace default acl_user by a GRUF one
        self.folder.manage_delObjects(['acl_users'])
        self.folder.manage_addProduct['GroupUserFolder'].manage_addGroupUserFolder()

        # Create a few roles
        self.folder._addRole("r1")
        self.folder._addRole("r2")
        self.folder._addRole("r3")

        # Create a few groups
        self.folder.acl_users._doAddGroup('g1', ())
        self.folder.acl_users._doAddGroup('g2', ('r1', ))
        self.folder.acl_users._doAddGroup('g3', ('r2', ))
        self.folder.acl_users._doAddGroup('g4', ('r2', 'r3', ))

        # Create a manager and a few users
        self.folder.acl_users._doAddUser('manager', 'secret', ('Manager',), (), (), )
        self.folder.acl_users._doAddUser('u1', 'secret', (), (), (), )
        self.folder.acl_users._doAddUser('u2', 'secret', (), (), ('g1', ), )
        self.folder.acl_users._doAddUser('u3', 'secret', (), (), ('g1', 'g2'), )
        self.folder.acl_users._doAddUser('u4', 'secret', (), (), ('g1', 'g2', 'g3'), )
        self.folder.acl_users._doAddUser('u5', 'secret', ('r1', ), (), ('g2', 'g3'), )
        self.folder.acl_users._doAddUser('u6', 'secret', ('r1', ), (), ('g3', ), )
        self.folder.acl_users._doAddUser('u7', 'secret', ('r1', ), (), ('g4', ), )

##        # Create a few folders to play with
        self.folder.manage_addProduct['OFSP'].manage_addFolder('lr')
        self.folder.lr.manage_addLocalRoles("group_g1", ("r3", ))
        self.folder.lr.manage_addLocalRoles("u3", ("r3", ))
        self.folder.lr.manage_addLocalRoles("u6", ("r3", ))
        Log(LOG_DEBUG, self.folder.lr.__ac_local_roles__)
        Log(LOG_DEBUG, self.folder.acl_users.getUser('group_g1').getRolesInContext(self.folder.lr))

##        # Need to commit so the ZServer threads see what we've done
##        get_transaction().commit()

##    def beforeClose(self):
##        # Commit after cleanup
##        get_transaction().commit()

    #                                                   #
    #           Basic GRUF behaviour testing            #
    #                                                   #

    def test01userRoles(self,):
        """
        test01userRoles => Test if the user "inherits" group roles
        """
        # Add a few roles
        self.folder._addRole("userrole")
        self.folder._addRole("grouprole")

        # Add the group & the user
        self.folder.acl_users._doAddGroup('gtest', ['grouprole'])
        self.folder.acl_users._doAddUser('utest', 'secret', ('userrole', ), (), ('gtest', ), )

        Log(LOG_DEBUG, self.folder.acl_users.getGroups())

        # Check if the user has the right roles
        usr = self.folder.acl_users.getUser('utest')
        roles = usr.getRoles()
        self.failUnless('Authenticated' in roles)
        self.failUnless('userrole' in roles)
        self.failUnless('grouprole' in roles)


    def compareRoles(self, target, user, roles):
        """
        compareRoles(self, target, user, roles) => do not raise if user has exactly the specified roles,
        else return a tuple (whished, actual).
        If target is None, test user roles (no local roles)
        """
        u = self.folder.acl_users.getUser(user)
        if target is None:
            actual_roles = filter(lambda x: x not in ('Authenticated',), list(u.getRoles()))
        else:
            actual_roles = filter(lambda x: x not in ('Authenticated',), list(u.getRolesInContext(target)))
            Log(LOG_DEBUG, "LR", target.getId(), user, actual_roles)
        actual_roles.sort()
        wished_roles = list(roles)
        wished_roles.sort()
        if actual_roles == wished_roles:
            return 1
        raise RuntimeError, "Wished roles: %s / Actual roles : %s" % (wished_roles, actual_roles)


    def test02securityMatrix(self,):
        """
        test02securityMatrix(self,) => Test the whole security matrix !

        We just check that people has the right roles
        """
        self.failUnless(self.compareRoles(None, "u1", ()))
        self.failUnless(self.compareRoles(None, "u2", ()))
        self.failUnless(self.compareRoles(None, "u3", ("r1", )))
        self.failUnless(self.compareRoles(None, "u4", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u5", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u6", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u7", ("r1", "r2", "r3", )))


    def test03localRoles(self,):
        """
        test03localRoles(self,) => Test the security matrix on a local role

        We just check that people has the right roles
        """
        self.failUnless(self.compareRoles(self.folder.lr, "u1", ()))
        self.failUnless(self.compareRoles(self.folder.lr, "u2", ("r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u3", ("r1", "r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u4", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u5", ("r1", "r2", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u6", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u7", ("r1", "r2", "r3", )))



    #                                                   #
    #               GRUF Interface testing              #
    #                                                   #

    def test03GRUFMethods(self,):
        """
        test03GRUFMethods(self,) => We test that GRUF's API is well protected
        """
        self.assertRaises(Unauthorized, self.folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')
        self.assertRaises(Unauthorized, self.folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')
        urllib.urlopen(base+'/acl_users/getGRUFId')


    #                                                   #
    #              Classical security testing           #
    #                                                   #


##    def testAccess(self):
##        '''Test access'''
##        page = self.folder.index_html(self.folder)

##    def testWeb(self):
##        '''Test web access'''
##        urllib._urlopener = UnauthorizedOpener()
##        page = urllib.urlopen(base+'/index_html').read()
##        if page.find('Resource not found') >= 0:
##            self.fail('Resource not found')

##    def testWeb2(self):
##        '''Test web access to protected resource'''
##        urllib._urlopener = ManagementOpener()
##        page = urllib.urlopen(base+'/secret_html').read()
##        if page.find('Resource not found') >= 0:
##            self.fail('Resource not found')
            
##    def testSecurity(self):
##        '''Test security of public resource'''
##        # Should be accessible
##        try: self.folder.restrictedTraverse('index_html')
##        except Unauthorized: self.fail('Unauthorized')

##    def testSecurity2(self):
##        '''Test security of protected resource'''
##        # Should be protected
##        self.assertRaises(Unauthorized, self.folder.restrictedTraverse, 'secret_html')
    
##    def testWebSecurity(self):
##        '''Test web security of public resource'''
##        # Should be accessible
##        urllib._urlopener = UnauthorizedOpener()
##        try: urllib.urlopen(base+'/index_html')
##        except Unauthorized: self.fail('Unauthorized')

##    def testWebSecurity2(self):
##        '''Test web security of protected resource'''
##        # Should be protected
##        urllib._urlopener = UnauthorizedOpener()
##        self.assertRaises(Unauthorized, urllib.urlopen, base+'/secret_html')

##    def testAbsoluteURL(self):
##        '''Test absolute_url'''
##        self.assertEquals(self.folder.absolute_url(), base)



if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestGroupUserFolder))
        return suite

