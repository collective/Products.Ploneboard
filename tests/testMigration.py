import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('CMFMember')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests.PloneTestCase import setupPloneSite as setupPloneSite
import Products.CMFPlone as CMFPlone
import Products.CMFCore as CMFCore
from Products.CMFMember.Extensions.Install import install as install_cmfmember
from Products.CMFMember.MemberDataContainer import MemberDataContainer
from Products.CMFMember.Member import Member
from Products.CMFMember.Extensions.Install import install as install_cmfmember
from Products.CMFMemberExample.Extensions.Install import install as install_cmfmemberexample
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName, ToolInit
from DateTime import DateTime
import string

usera = {'id':'a','password':'123', 'roles':('Member',), 'domains':('127.0.0.1',), 'email':'A', 'fullname':'A Fuler'}
userb = {'id':'b', 'password':'456', 'roles':('Member','Reviewer',), 'domains':(), 'email':'B', 'fullname':'B Fuler'}


from Products.CMFMember.utils import TYPESMAP

PropTypes = TYPESMAP.keys()

stringies = (
    'ustring',
    'text',
    'utext',
    'string'
    )

testtext = "Blah Blah Blah Blah Blah"

populator_choices = ('A', 'B', 'C', 'D', 'E', 'F')
populator = string.join(populator_choices, '\n')

test_seq= ('tweedle','deedle', 'dum')
lines_data = string.join(test_seq, '\n')
tokens_data = string.join(test_seq)
prop_data = tuple(\
    [(x, testtext) for x in stringies]) + (
    (('date', '01/01/1900'), '12/31/1999'), 
    (('float', 0), 1.5),
    (('long', 0), 10000000000000000000000000000000000000),
    (('int', 0), 1),
    (('multiple selection', 'populator'), populator_choices[::2]),
    (('selection', 'populator'), populator_choices[:-1]),
    ('boolean', True),
    ('lines', lines_data),
    ('ulines', lines_data),
    ('tokens', tokens_data),
    ('utokens', tokens_data)\
    )

propName = lambda proptype: '%s_prop' % string.join(proptype.split(), '_')
class TestMigration( PloneTestCase.PloneTestCase ):

    def defaultsDict(self):
        return dict([x for x in dict(prop_data).keys() if type(x) == type((0,))])

    def populateDict(self):
        with_defaults = dict(\
            [(propName(defaults[0]), data) \
             for defaults, data in prop_data if type(defaults) == type((0,))])

        wo_defaults   = dict(\
            [(propName(proptype), data) \
             for proptype, data in prop_data if type(proptype) != type((0,))])

        with_defaults.update(wo_defaults)
        return with_defaults

    def testMigrationPlone2CMFMember(self):
        self.makeMembers()

        mdtool = self.portal.portal_memberdata
        mstool = self.portal.portal_membership

        # check that we have what we should have before migration
        self.assertEquals(self.portal.portal_memberdata.__class__, CMFPlone.MemberDataTool.MemberDataTool)
        
        self._compare_members()

        # add new properties to MemberData tool
        addprop = mdtool.manage_addProperty
        
        addprop('populator', populator, 'lines')
        defaults = self.defaultsDict()

        join = string.join
        for proptype in PropTypes:
            name, default, proptype = ( propName(proptype), '', proptype)
            if defaults.has_key(proptype):
                default = defaults[proptype]
            addprop(name, default, proptype)

        user_a = mstool.getMemberById(usera['id'])
        populate = self.populateDict()
        
        user_a.manage_changeProperties(**populate)

        # verify that the properties exists

        errors = self.compareProperties(user_a)
        self.failIf(len(errors) > 0, string.join(errors, '\n'))

        # Install CMFMember, migrate Plone member stuff to CMFMember
        install_cmfmember(self.portal)
        self.portal.cmfmember_control.upgrade(swallow_errors=0)

        mdtool = self.portal.portal_memberdata
        mstool = self.portal.portal_membership

        self.assertEquals(self.portal.portal_memberdata.__class__, MemberDataContainer)
        self.assertEquals(mstool.getMemberById(usera['id']).__class__, Member)
        self.assertEquals(mstool.getMemberById(userb['id']).__class__, Member)

        a = mstool.getMemberById(usera['id'])
        self._compare_members()

        errors = self.compareProperties(user_a)
        self.failIf(len(errors) > 0, string.join(errors, '\n'))

    def compareProperties(self, md):
        data = self.populateDict()
        md_data = ()
        if md.__class__ == Member:
            schema = md.schema()
            md_data = [ ( x, x.getAccessor()() ) for x in schema.fields()] 
        else:
            md_data = [ ( x, md.getProperty(x))  for x in data.keys() ] 

        # some properties are returned from the member data object
        # in a different format than we passed them in... this weirdness
        # below is just massaging the data back into its original state
        # so we can compare it correctly
        newlines = lambda x: string.join(x, '\n')
        spaces   = lambda x: string.join(x, ' ')
        dates    = lambda x: x.strftime('%m/%d/%Y')
        
        func_map = (
            ('lines_prop', newlines),
            ('ulines_prop', newlines),
            ('tokens_prop', spaces),
            ('utokens_prop', spaces),
            ('date_prop',  dates),
            )
        
        func_map = dict(func_map)
        tmp  = []
        for name, val in md_data:
            if func_map.has_key(name):
                newval = func_map[name](val)
                tmp.append((name, newval))
            else:
                tmp.append((name, val))

        md_data = dict(tmp)
        
        def getProp(prop):
            val = None
            if md_data.has_key(prop):
                val = md_data[prop]
            return val

        # Check raw data
        errors = [ "%s %s != %s" %(x, getProp(x), data[x]) for x in data.keys() if getProp(x) != data[x] ]
        return errors

            
    def _compare_members(self):
        membership_tool = self.portal.portal_membership
        def props(md, ud):
            return (
                (md.getMemberId(),           ud['id']),
                (md.getPassword(),           ud['password']),
                (md.getUser().getRoles(),    ud['roles'] + ('Authenticated',)),
                (md.getDomains(),            ud['domains']),
                (md.getProperty('email'),    ud['email']),
                (md.getProperty('fullname'), ud['fullname']),
                )
                    
        a_props = dict(props(membership_tool.getMemberById(usera['id']),  usera))
        b_props = dict(props(membership_tool.getMemberById(userb['id']),  userb))
        
        self.assertEqual(a_props.keys(), a_props.values())
        self.assertEqual(b_props.keys(), b_props.values())        

    def afterSetUp( self ):
        # create an admin user
        #self.portal.acl_users.userFolderAddUser('test_admin', 'qwerty', ('Manager','Member',), ())
        #import pdb; pdb.set_trace()
        #get_transaction().commit(1)
        # assume role of test_admin
        self.loginPortalOwner()
            
        #newSecurityManager(None, self.portal.acl_users.getUser('test_admin').__of__(self.portal.acl_users))

    def makeMembers(self):
        membership_tool = self.portal.portal_membership
        membership_tool.addMember(usera['id'], usera['password'], usera['roles'], usera['domains'])
        user_a = membership_tool.getMemberById(usera['id'])
        user_a.setMemberProperties({'email':usera['email'],
                               'fullname':usera['fullname']})

        membership_tool.addMember(userb['id'], userb['password'], userb['roles'], userb['domains'])
        user_b = membership_tool.getMemberById(userb['id'])
        user_b.setMemberProperties({'email':userb['email'],
                               'fullname':userb['fullname']})

        
    def xtestMigrationPlone2CMFMember(self):
        self.makeMembers()
        # check that we have what we should have before migration
        self.assertEquals(self.portal.portal_memberdata.__class__, CMFPlone.MemberDataTool.MemberDataTool)
        self._compare_members()

        install_cmfmember(self.portal)
        # migrate Plone member stuff to CMFMember
        self.portal.cmfmember_control.upgrade(swallow_errors=False)

        # check that we still have everything we had before
        
        self.assertEquals(self.portal.portal_memberdata.__class__, MemberDataContainer)
        self._compare_members()
        
        self.assertEquals(self.portal.portal_memberdata.a.__class__, Member)
        self.assertEquals(self.portal.portal_memberdata.b.__class__, Member)

if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestMigration))
        return suite
