#                                                       #
#                 Test GroupUserFolder                  #
#                                                       #
#                                                       #
# (c)2002-2004 Ingeniweb                                #


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



# Set log options if Log module is available
# This is done to set LOG_PROCESSORs to file logs instead of Zope logs
try:
    import Log

    Log.LOG_LEVEL = Log.LOG_DEBUG

    Log.LOG_PROCESSOR = {
        Log.LOG_NONE: Log.LogFile,
        Log.LOG_CRITICAL: Log.LogFile,
        Log.LOG_ERROR: Log.LogFile,
        Log.LOG_WARNING: Log.LogFile,
        Log.LOG_NOTICE: Log.LogFile,
        Log.LOG_DEBUG: Log.LogFile,
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


class GRUFTestCase(ZopeTestCase.ZopeTestCase):

    def gruf_setup(self,):
        """
        gruf_setup(self,) => Basic gruf setup
        """
        # Replace default acl_user by a GRUF one
        self.folder.manage_delObjects(['acl_users'])
        self.folder.manage_addProduct['OFSP'].manage_addFolder('testFolder')
        self.gruf_folder = self.folder.testFolder
        self.gruf_folder.manage_addProduct['GroupUserFolder'].manage_addGroupUserFolder()
        self.gruf = self.gruf_folder.acl_users


    def gruf_sources_setup(self,):
        """
        gruf_sources_setup(self,) => this method installs the required sources inside GRUF.
        One can override this in a test case to install other sources and make another bunch of unit tests
        For example, for LDAPUserFolder, use manage_addProduct/LDAPUserFolder/addLDAPUserFolder
        """
        # Use this to replace the default user source
        self.gruf.replaceUserSource("Users", "manage_addProduct/OFSP/manage_addUserFolder")

        # Use this to replace the default group source
        self.gruf.replaceUserSource("Groups", "manage_addProduct/OFSP/manage_addUserFolder")

    def security_context_setup(self,):
        """
        Build a complex security environment

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
        # Create a few roles
        self.gruf.userFolderAddRole("r1")
        self.gruf.userFolderAddRole("r2")
        self.gruf.userFolderAddRole("r3")

        # Setup users and groups
        self.security_context_setup_groups()
        self.security_context_setup_users()
        
        # Create a few folders to play with
        self.gruf_folder.manage_addProduct['OFSP'].manage_addFolder('lr')
        self.gruf_folder.lr.manage_addLocalRoles("group_g1", ("r3", ))
        self.gruf_folder.lr.manage_addLocalRoles("u3", ("r3", ))
        self.gruf_folder.lr.manage_addLocalRoles("u6", ("r3", ))


    def security_context_setup_users(self,):
        # Create a manager and a few users
        self.gruf.userFolderAddUser('manager', 'secret', ('Manager',), (), (), )
        self.gruf.userFolderAddUser('u1', 'secret', (), (), (), )
        self.gruf.userFolderAddUser('u2', 'secret', (), (), ('g1', ), )
        self.gruf.userFolderAddUser('u3', 'secret', (), (), ('g1', 'g2'), )
        self.gruf.userFolderAddUser('u4', 'secret', (), (), ('g1', 'g2', 'g3'), )
        self.gruf.userFolderAddUser('u5', 'secret', ('r1', ), (), ('g2', 'g3'), )
        self.gruf.userFolderAddUser('u6', 'secret', ('r1', ), (), ('g3', ), )
        self.gruf.userFolderAddUser('u7', 'secret', ('r1', ), (), ('g4', ), )

        # Create nested-groups users
        self.gruf.userFolderAddUser('u8', 'secret', (), (), ('ng1', ), )        
        self.gruf.userFolderAddUser('u9', 'secret', (), (), ('g1', 'ng2', ), )
        self.gruf.userFolderAddUser('u10', 'secret', (), (), ('ng2', 'ng3', ), )        
        self.gruf.userFolderAddUser('u11', 'secret', ('r3', ), (), ('ng2', 'ng3', ), )        
##        self.gruf.userFolderAddUser('u12', 'secret', (), (), ('ng5', 'ng6', ), )        

    def security_context_setup_groups(self,):
        "create groups. We splitted to allow LDAP tests to override this"
        # Create a few groups
        self.gruf.userFolderAddGroup('g1', ())
        self.gruf.userFolderAddGroup('g2', ('r1', ))
        self.gruf.userFolderAddGroup('g3', ('r2', ))
        self.gruf.userFolderAddGroup('g4', ('r2', 'r3', ))

        # Create nested groups
        self.gruf.userFolderAddGroup('ng1', (), ('g1', ))
        self.gruf.userFolderAddGroup('ng2', (), ('g2', 'g3', ))
        self.gruf.userFolderAddGroup('ng3', (), ('g2', 'ng2', ))
        self.gruf.userFolderAddGroup('ng4', ('r3', ), ('g2', 'ng2', ))
        self.gruf.userFolderAddGroup('ng5', (), ('g2', 'ng4', ))
##        self.gruf.userFolderAddGroup('ng6', (), ('ng5', 'ng6', ))

        # Special case of nesting
        self.gruf.userFolderAddGroup('extranet', (), ())
        self.gruf.userFolderAddGroup('intranet', (), ('extranet', ))
        self.gruf.userFolderAddGroup('compta', (), ('intranet', 'extranet' ))


    def afterSetUp(self,):
        """
        afterSetUp(self) => This method is called to create Folder with a GRUF inside.
        """
        self.gruf_setup()
        self.gruf_sources_setup()
        self.security_context_setup()
##        # Need to commit so the ZServer threads see what we've done
##        get_transaction().commit()



    def beforeClose(self):
##        # Commit after cleanup
##        get_transaction().commit()

        # Remove users. This may be useful for non-ZODB user sources.
        self.delete_created_users()

    def delete_created_users(self,):
        self.gruf.userFolderDelUsers([
            "manager",
            "u1",
            "u2",
            "u3",
            "u4",
            "u5",
            "u6",
            "u7",
            "u8",
            "u9",
            "u10",
            "u11",
            "created_user",
            "group_test_prefix",
            "test_prefix",
            ])
        self.gruf.userFolderDelGroups([
            "g1",
            "g2",
            "g3",
            "g4",
            "ng1",
            "ng2",
            "ng3",
            "ng4",
            "ng5",
            "extranet",
            "intranet",
            "compta",
            ])

    def compareRoles(self, target, user, roles):
        """
        compareRoles(self, target, user, roles) => do not raise if user has exactly the specified roles.
        If target is None, test user roles (no local roles)
        """
        u = self.gruf.getUser(user)
        if not u:
            raise RuntimeError, "compareRoles: Invalid user: '%s'" % user
        if target is None:
            actual_roles = filter(lambda x: x not in ('Authenticated', 'Anonymous', ''), list(u.getRoles()))
        else:
            actual_roles = filter(lambda x: x not in ('Authenticated', 'Anonymous', ''), list(u.getRolesInContext(target)))
        actual_roles.sort()
        wished_roles = list(roles)
        wished_roles.sort()
        if actual_roles == wished_roles:
            return 1
        raise RuntimeError, "User %s: Whished roles: %s BUT current roles: %s" % (user, wished_roles, actual_roles)


    def compareGroups(self, user, groups):
        """
        compareGroups(self, user, groups) => do not raise if user has exactly the specified groups.
        """
        u = self.gruf.getUser(user)
        if not u:
            raise RuntimeError, "compareGroups: Invalid user: '%s'" % user
        actual_groups = list(u.getGroups())
        actual_groups.sort()
        wished_groups = map(lambda x: "group_%s" % x, list(groups))
        wished_groups.sort()
        if actual_groups == wished_groups:
            return 1
        raise RuntimeError, "User %s: Whished groups: %s BUT current groups: %s" % (user, wished_groups, actual_groups)


