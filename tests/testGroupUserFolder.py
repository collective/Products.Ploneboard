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
          * two roles, role1 and role2, with no particular permissions
          * two groups: group1 having role1 perm and group2 having role2 perm
          * three users called 'testuser', 'testuser_g1' and 'testuser_g1_g2'.

        Then we create a few folders with the following permissions matrix:
                group1          group2          role1           role2           Mgr
                (LocalRole)     (LocalRole)     (Perms)         (Perms)
                ===================================================================
        a                                                                       R,W
        b                                       R                               R,W
        c       role1                           R                               R,W
        
        """
        # Replace default acl_user by a GRUF one
        self.folder.manage_delObjects(['acl_users'])
        self.folder.manage_addProduct['GroupUserFolder'].manage_addGroupUserFolder()

        # Create a few roles
        self.folder._addRole("role1")
        self.folder._addRole("role2")
        self.folder._addRole("role2")
        self.folder._addRole("role_test")

        # Create a few groups
        self.folder.acl_users._doAddGroup('group1', ['role1'])
        self.folder.acl_users._doAddGroup('group2', ['role2'])
        self.folder.acl_users._doAddGroup('grouptest', ['roletest'])

        # Create a manager and a few users
        self.folder.acl_users._doAddUser('manager', 'secret', ('Manager',), (), )
        self.folder.acl_users._doAddUser('testuser', 'secret', (), (), )
        self.folder.acl_users._doAddUser('testuser_g1', 'secret1', ('Manager',), (), )
        self.folder.acl_users._doAddUser('testuser_g2', 'secret2', ('Manager',), (), )

        # Create a few folders to play with
        self.folder.manage_addProduct['OFSP'].manage_addFolder('a')
        self.folder.manage_addProduct['OFSP'].manage_addFolder('b')
        self.folder.manage_addProduct['OFSP'].manage_addFolder('c')
        self.folder.b.manage_addLocalRoles("group1", "role_test")

        # Create a few documents to play with
        self.folder.addDTMLMethod('index_html', file='index_html: <dtml-var objectIds>')
        self.folder.addDTMLMethod('secret_html', file='secret_html: <dtml-var objectIds>')

        # Lock down secret_html
        s = self.folder.secret_html
        for p in ZopeTestCase._standard_permissions:
            s.manage_permission(p, ['Manager'], acquire=0)

        # Need to commit so the ZServer threads see what we've done
        get_transaction().commit()


    def beforeClose(self):
        # Commit after cleanup
        get_transaction().commit()



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

    def test02securityMatrix(self,):
        """
        test02securityMatrix(self,) => Test the whole security matrix !

        We just check that people has the right roles
        """
        pass


    #                                                   #
    #              Classical security testing           #
    #                                                   #

    def testAccess(self):
        '''Test access'''
        page = self.folder.index_html(self.folder)

    def testWeb(self):
        '''Test web access'''
        urllib._urlopener = UnauthorizedOpener()
        page = urllib.urlopen(base+'/index_html').read()
        if page.find('Resource not found') >= 0:
            self.fail('Resource not found')

    def testWeb2(self):
        '''Test web access to protected resource'''
        urllib._urlopener = ManagementOpener()
        page = urllib.urlopen(base+'/secret_html').read()
        if page.find('Resource not found') >= 0:
            self.fail('Resource not found')
            
    def testSecurity(self):
        '''Test security of public resource'''
        # Should be accessible
        try: self.folder.restrictedTraverse('index_html')
        except Unauthorized: self.fail('Unauthorized')

    def testSecurity2(self):
        '''Test security of protected resource'''
        # Should be protected
        self.assertRaises(Unauthorized, self.folder.restrictedTraverse, 'secret_html')
    
    def testWebSecurity(self):
        '''Test web security of public resource'''
        # Should be accessible
        urllib._urlopener = UnauthorizedOpener()
        try: urllib.urlopen(base+'/index_html')
        except Unauthorized: self.fail('Unauthorized')

    def testWebSecurity2(self):
        '''Test web security of protected resource'''
        # Should be protected
        urllib._urlopener = UnauthorizedOpener()
        self.assertRaises(Unauthorized, urllib.urlopen, base+'/secret_html')

    def testAbsoluteURL(self):
        '''Test absolute_url'''
        self.assertEquals(self.folder.absolute_url(), base)



if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestGroupUserFolder))
        return suite

