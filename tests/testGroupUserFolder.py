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


        And then, it creates nested groups as follow (-> = belongs to group...):

             u/g   !  belongs to... ! resulting roles                     !
         ----------!----------------!-------------------------------------!
          ng1      !   g1           ! (no role)                           !
          ng2      !   g2, g3       ! r1, r2                              !
          ng3      !   g2, ng2      ! r1, r2                              !
          ng4(r3)  !   g2, ng2      ! r1, r2, r3                          !
          ng5      !   g2, ng4      ! r1, r2, r3                          !
          ng6      !   ng5, ng6     ! r1, r2, r3 (no circ. ref)           !
          u8       !   ng1          ! (no role)                           !
          u9       !   g1, ng2      ! r1, r2                              !
          u10      !   ng2, ng3     ! r1, r2                              !
          u11(r3)  !   ng2, ng3     ! r1, r2, r3                          !
          u12      !   ng5, ng6     ! r1, r2, r3                          !
         -----------------------------------------------------------------!

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

        # Create nested groups
        self.folder.acl_users._doAddGroup('ng1', (), ('g1', ))
        self.folder.acl_users._doAddGroup('ng2', (), ('g2', 'g3', ))
        self.folder.acl_users._doAddGroup('ng3', (), ('g2', 'ng2', ))
        self.folder.acl_users._doAddGroup('ng4', ('r3', ), ('g2', 'ng2', ))
        self.folder.acl_users._doAddGroup('ng5', (), ('g2', 'ng4', ))
##        self.folder.acl_users._doAddGroup('ng6', (), ('ng5', 'ng6', ))

        # Create a manager and a few users
        self.folder.acl_users._doAddUser('manager', 'secret', ('Manager',), (), (), )
        self.folder.acl_users._doAddUser('u1', 'secret', (), (), (), )
        self.folder.acl_users._doAddUser('u2', 'secret', (), (), ('g1', ), )
        self.folder.acl_users._doAddUser('u3', 'secret', (), (), ('g1', 'g2'), )
        self.folder.acl_users._doAddUser('u4', 'secret', (), (), ('g1', 'g2', 'g3'), )
        self.folder.acl_users._doAddUser('u5', 'secret', ('r1', ), (), ('g2', 'g3'), )
        self.folder.acl_users._doAddUser('u6', 'secret', ('r1', ), (), ('g3', ), )
        self.folder.acl_users._doAddUser('u7', 'secret', ('r1', ), (), ('g4', ), )

        # Create nested-groups users
        self.folder.acl_users._doAddUser('u8', 'secret', (), (), ('ng1', ), )        
        self.folder.acl_users._doAddUser('u9', 'secret', (), (), ('g1', 'ng2', ), )
        self.folder.acl_users._doAddUser('u10', 'secret', (), (), ('ng2', 'ng3', ), )        
        self.folder.acl_users._doAddUser('u11', 'secret', ('r3', ), (), ('ng2', 'ng3', ), )        
##        self.folder.acl_users._doAddUser('u12', 'secret', (), (), ('ng5', 'ng6', ), )        

        # Create a few folders to play with
        self.folder.manage_addProduct['OFSP'].manage_addFolder('lr')
        self.folder.lr.manage_addLocalRoles("group_g1", ("r3", ))
        self.folder.lr.manage_addLocalRoles("u3", ("r3", ))
        self.folder.lr.manage_addLocalRoles("u6", ("r3", ))

        # Special case of nesting
        self.folder.acl_users._doAddGroup('extranet', (), ())
        self.folder.acl_users._doAddGroup('intranet', (), ('extranet', ))
        self.folder.acl_users._doAddGroup('compta', (), ('intranet', 'extranet' ))

##        # Need to commit so the ZServer threads see what we've done
##        get_transaction().commit()

##    def beforeClose(self):
##        # Commit after cleanup
##        get_transaction().commit()

    #                                                   #
    #           Basic GRUF behaviour testing            #
    #                                                   #

    def test00userNames(self,):
        """
        test00userNames(self,)
        Basic test of user and group names.
        """
        un = self.folder.acl_users.getUserNames()
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))
        

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

        # Check if the user has the right roles
        usr = self.folder.acl_users.getUser('utest')
        roles = usr.getRoles()
        self.failUnless('Authenticated' in roles)
        self.failUnless('userrole' in roles)
        self.failUnless('grouprole' in roles)


    def compareRoles(self, target, user, roles):
        """
        compareRoles(self, target, user, roles) => do not raise if user has exactly the specified roles.
        If target is None, test user roles (no local roles)
        """
        u = self.folder.acl_users.getUser(user)
        if not u:
            raise RuntimeError, "compareRoles: Invalid user: '%s'" % user
        if target is None:
            actual_roles = filter(lambda x: x not in ('Authenticated',), list(u.getRoles()))
        else:
            actual_roles = filter(lambda x: x not in ('Authenticated',), list(u.getRolesInContext(target)))
        actual_roles.sort()
        wished_roles = list(roles)
        wished_roles.sort()
        if actual_roles == wished_roles:
            return 1
        raise RuntimeError, "User %s: Wished roles: %s BUT current roles: %s" % (user, wished_roles, actual_roles)


    def compareGroups(self, user, groups):
        """
        compareGroups(self, user, groups) => do not raise if user has exactly the specified groups.
        """
        u = self.folder.acl_users.getUser(user)
        if not u:
            raise RuntimeError, "compareGroups: Invalid user: '%s'" % user
        actual_groups = list(u.getGroups())
        actual_groups.sort()
        wished_groups = map(lambda x: "group_%s" % x, list(groups))
        wished_groups.sort()
        if actual_groups == wished_groups:
            return 1
        raise RuntimeError, "User %s: Wished groups: %s BUT current groups: %s" % (user, wished_groups, actual_groups)


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


    def test03usersBelongToGroups(self,):
        """
        test03usersBelongToGroups(self,) => test that the users belong to the right groups.
        This implies nested groups testing
        """
        # Check regular users
        self.failUnless(self.compareGroups("u1", ()))
        self.failUnless(self.compareGroups("u2", ("g1", )))
        self.failUnless(self.compareGroups("u3", ("g1", "g2", )))
        self.failUnless(self.compareGroups("u4", ("g1", "g2", "g3", )))
        self.failUnless(self.compareGroups("u5", ("g2", "g3", )))
        self.failUnless(self.compareGroups("u6", ("g3", )))
        self.failUnless(self.compareGroups("u7", ("g4", )))

        # Check nested groups
        self.failUnless(self.compareGroups("group_ng1", ("g1", )))
        self.failUnless(self.compareGroups("group_ng2", ("g2", "g3", )))
        self.failUnless(self.compareGroups("group_ng3", ("g2", "g3", "ng2", )))
        self.failUnless(self.compareGroups("group_ng4", ("g2", "g3", "ng2", )))
        self.failUnless(self.compareGroups("group_ng5", ("g2", "g3", "ng2", "ng4", )))
##        self.failUnless(self.compareGroups("ng6", ("ng5", )))

        # Check nested-groups users
        self.failUnless(self.compareGroups("u8", ("ng1", "g1", )))
        self.failUnless(self.compareGroups("u9", ("ng2", "g1", "g2","g3",  )))
        self.failUnless(self.compareGroups("u10", ("ng2", "ng3", "g2", "g3", )))
        self.failUnless(self.compareGroups("u11", ("ng2", "ng3", "g2", "g3", )))
##        self.failUnless(self.compareGroups("u12", ()))


    def test04localRoles(self,):
        """
        Test the security matrix on a local role

        We just check that people has the right roles
        """
        self.failUnless(self.compareRoles(self.folder.lr, "u1", ()))
        self.failUnless(self.compareRoles(self.folder.lr, "u2", ("r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u3", ("r1", "r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u4", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u5", ("r1", "r2", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u6", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u7", ("r1", "r2", "r3", )))


    def test05nestedGroups(self,):
        """
        Test security on nested groups
        """
        # Test group roles
        self.failUnless(self.compareRoles(None, "group_ng1", ()))
        self.failUnless(self.compareRoles(None, "group_ng2", ('r1', 'r2', )))
        self.failUnless(self.compareRoles(None, "group_ng3", ('r1', 'r2', )))
        self.failUnless(self.compareRoles(None, "group_ng4", ('r1', 'r2', 'r3', )))
        self.failUnless(self.compareRoles(None, "group_ng5", ('r1', 'r2', 'r3', )))
##        self.failUnless(self.compareRoles(None, "group_ng6", ()))

        # Test user roles
        self.failUnless(self.compareRoles(None, "u8", ()))
        self.failUnless(self.compareRoles(None, "u9", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u10", ("r1", "r2", )))
        self.failUnless(self.compareRoles(None, "u11", ("r1", "r2", "r3")))
##        self.failUnless(self.compareRoles(None, "u12", ("r1", "r2", "r3")))

        # Test the same with local roles (wow !)
        self.failUnless(self.compareRoles(self.folder.lr, "u8", ("r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u9", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u10", ("r1", "r2", )))
        self.failUnless(self.compareRoles(self.folder.lr, "u11", ("r1", "r2", "r3")))
##        self.failUnless(self.compareRoles(self.folder.lr, "u12", ("r1", "r2", "r3")))


    def test06doubleNesting(self,):
        """
        Test against double nesting
        """
        self.failUnless(self.compareGroups("group_compta", ('intranet', 'extranet', )))
    

    #                                                   #
    #               GRUF Interface testing              #
    #                                                   #

    def test10GRUFMethods(self,):
        """
        We test that GRUF's API is well protected
        """
        self.assertRaises(Unauthorized, self.folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')
        self.assertRaises(Unauthorized, self.folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')
        urllib.urlopen(base+'/acl_users/getGRUFId')


    def test11GRUFAPI(self,):
        """
        Test that gruf API for adding, removing and changing users and groups is okay
        """
        pass            # XXX TODO


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

