from Testing import ZopeTestCase

# Add products/dependencies here as needed
ZopeTestCase.installProduct('CMFMember')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('ZCatalog')
    
from Products.CMFPlone.tests import PloneTestCase
from Products.Archetypes.Extensions.Install import install as install_archetypes
from Products.CMFMember.Extensions.Install import install as install_cmfmember
from AccessControl.SecurityManagement import newSecurityManager

portal_name  = 'portal'
portal_owner = 'portal_owner'

default_user = 'unittest_admin'

app = ZopeTestCase.app()
portal = app[portal_name]
uf = portal.acl_users

# create a portal administrator
admin_user_info = {'id':default_user, 'password':'password', 'roles':('Manager','Member',), 'domains':()}
uf._doAddUser(admin_user_info['id'], admin_user_info['password'], admin_user_info['roles'], [])
admin_user = uf.getUserById(admin_user_info['id'])
# set aquisition context for admin_user
if not hasattr(admin_user, 'aq_base'):
    admin_user = admin_user.__of__(uf)

# create a user in the portal's acl_users folder
portal_user_info = {'id':'unittest_user', 'password':'secret', 'roles':('Member',), 'domains':()}
uf._doAddUser(portal_user_info['id'], portal_user_info['password'], portal_user_info['roles'], [])
portal_user = uf.getUserById(portal_user_info['id'])
# set aquisition context for portal_user
if not hasattr(portal_user, 'aq_base'):
    portal_user = portal_user.__of__(uf)

# create a user in the zope root's acl_users folder
root_user_info = {'id':'unittest_root_user', 'password':'password2', 'roles':('Manager',), 'domains':()}
app.acl_users._doAddUser(root_user_info['id'], root_user_info['password'], root_user_info['roles'], [])
root_user = app.acl_users.getUserById(root_user_info['id'])
# set aquisition context for root_user
if not hasattr(root_user, 'aq_base'):
    root_user = root_user.__of__(app.acl_users)

newSecurityManager(None, admin_user)

# # add a member corresponding to portal_user
# portal.portal_membership.addMember(portal_user_info['id'], portal_user_info['password'],portal_user_info['roles'],portal_user_info['domains'])
# m = portal.portal_membership.getMemberById(portal_user_info['id'])
# m.setMemberProperties({'email': 'foo@bar.com'})

# portal.acl_users._doAddUser(root_user_info['id'], root_user_info['password'],domains=root_user_info['domains'],roles=root_user_info['roles'])
# m = portal.portal_membership.getMemberById(root_user_info['id'])
# m.setMemberProperties({'email': 'foo@bar.com'})

get_transaction().commit()
install_cmfmember(app[portal_name])
portal.cmfmember_control.upgrade()
get_transaction().commit()
ZopeTestCase.close(app)


class CMFMemberTestCase(PloneTestCase.PloneTestCase):

    admin_user_info = admin_user_info
    admin_user = admin_user
    
    portal_user_info = portal_user_info
    portal_user = portal_user
    
    root_user_info = root_user_info
    root_user = root_user


    def compareTuples(self, t1, t2):
        t1 = list(t1)
        t1.sort()
        t2 = list(t2)
        t2.sort()
        return t1 == t2
        

    def createUserContent(self):
        # create some content with interesting ownership structure
        # portal.folder1 is owned by portal_user;
        #   root_user has the local role Reviewer in portal.folder1
        #   portal.folder1.doc1 is owned by portal_user
        #   portal.folder1.doc2 is owned by root_user
        # 
        # portal.folder2 is owned by root_user;
        #   portal_user has the local role Reviewer in portal.folder2
        #   portal.folder2.doc3 is owned by portal_user
        #   portal.folder2.doc4 is owned by root_user
        self.portal.invokeFactory(id='folder1', type_name='Folder')
        folder1 = self.portal['folder1']
        folder1.changeOwnership(self.portal_user)
        folder1.manage_addLocalRoles(self.root_user.getUserName(), ('Reviewer',))
        
        folder1.invokeFactory(id='doc1', type_name='Document')
        doc1 = getattr(folder1, 'doc1')
        doc1.changeOwnership(self.portal_user)

        folder1.invokeFactory(id='doc2', type_name='Document')
        doc2 = getattr(folder1, 'doc2')
        doc2.changeOwnership(self.root_user)

        self.portal.invokeFactory(id='folder2', type_name='Folder')
        folder2 = self.portal['folder2']
        folder2.changeOwnership(self.root_user)
        folder2.manage_addLocalRoles(self.portal_user.getUserName(), ('Reviewer',))

        folder2.invokeFactory(id='doc3', type_name='Document')
        doc3 = getattr(folder2, 'doc3')
        doc3.changeOwnership(self.portal_user)

        folder2.invokeFactory(id='doc4', type_name='Document')
        doc4 = getattr(folder2, 'doc4')
        doc4.changeOwnership(self.root_user)

        # recatalog to make sure catalog knows about new local roles and ownership
        catalog = portal.portal_catalog
        catalog.refreshCatalog(clear=1)
        
    def afterSetUp(self): 
        self.qi = self.portal.portal_quickinstaller
        self.membership = self.portal.portal_membership
        self.memberdata = self.portal.portal_memberdata
        self.setRoles(['Manager'])

    def getTheTag(self, pParser, tag, **kwargs):
        if not tag: return None
        if not kwargs: return pParser.get_tag(tag)

        for token in pParser.tags(tag):
            if token.type == "endtag": continue
            attributeMatch = 0
            for attribute in kwargs.keys():
                if dict(token.attrs).get(attribute, "-") == kwargs[attribute]:
                    attributeMatch = 1
                else:
                    attributeMatch = 0
            if attributeMatch:
                return pParser.get_compressed_text(endat=("endtag", tag))
        return None


    def addUsers(self):
        # Used for functional testin since users have to be added after
        # the server started
        uf = self.portal.acl_users

        # create a portal administrator
        admin_user_info = {'id':default_user, 'password':'password', 'roles':('Manager','Member',), 'domains':()}
        uf._doAddUser(admin_user_info['id'], admin_user_info['password'], admin_user_info['roles'], [])
        admin_user = uf.getUserById(admin_user_info['id'])
        # set aquisition context for admin_user
        if not hasattr(admin_user, 'aq_base'):
            admin_user = admin_user.__of__(uf)

        # create a user in the portal's acl_users folder
        portal_user_info = {'id':'unittest_user', 'password':'secret', 'roles':('Member',), 'domains':()}
        uf._doAddUser(portal_user_info['id'], portal_user_info['password'], portal_user_info['roles'], [])
        portal_user = uf.getUserById(portal_user_info['id'])
        # set aquisition context for portal_user
        if not hasattr(portal_user, 'aq_base'):
            portal_user = portal_user.__of__(uf)

