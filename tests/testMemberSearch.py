import os, sys, string
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFMember.tests import CMFMemberTestCase

email = 'bobby@bobby.com'

fullnames = ('Bob Barker', '3rd Base', 'ActionGrl', 'Rhonda', 'Tom', 'Dick', 'Harry', 'Melinda', 'Shanikqua', 'Jane', 'Crystal', 'Yolanda', 'Elvis', 'Alfred E. Neuman', 'Zamfir X')

query = {'getId':'0member', 'getFullname':'Bob Barker', 'getEmail':email}

class TestMemberSearch(CMFMemberTestCase.CMFMemberTestCase):
    
    def afterSetUp(self):
        CMFMemberTestCase.CMFMemberTestCase.afterSetUp( self )
        self.addTestMembers() # makes 3 more users
        
    def testInstallationofMemberCatalog(self):
        self.failUnless(hasattr(self.portal, 'member_catalog'))
        self.failUnless('review_state' in self.portal.member_catalog.indexes())
        cat_indexes = self.portal.member_catalog.indexes()
        schema = self.portal.archetype_tool.lookupType('CMFMember','Member')['schema']
        accessors = [x.accessor  for x in schema.fields() if x.index]
        accessors.append('review_state')
        accessors.sort()
        cat_indexes.sort()
        self.assertEqual(cat_indexes, accessors)

    def testKWSearchForMembers(self):
        results = self.memberdata.searchForMembers(getId='0member', getFullname='Bob Barker', getEmail=email, brains='yes_please')
        self.assertEquals(results[0].getFullname, 'Bob Barker')

    def testReturn(self):
        # with brains
        request = self.app.REQUEST
        request.set('brains', True)
        request.form = query
        results = self.memberdata.searchForMembers(request)
        self.assertEquals([x.getId for x in results], ['0member'])
        self.assertEquals([x.getFullname for x in results], ['Bob Barker'])
        
        # brainless(objects)
        request.set('brains', False)
        results = self.memberdata.searchForMembers(request)
        self.assertEquals([x.getFullname() for x in results], ['Bob Barker'])

    def testSearchForMembers(self):
        # can we search at all?
        request = self.app.REQUEST
        request.set('brains', 'yes please!')
        search = self.memberdata.searchForMembers(request)
        
        from sets import Set
        test_set    = Set([x.getId for x in search])
        control_set = Set(['0member', '1member', '2member'])
        self.failUnless( control_set.issubset(test_set), "Isn't subset control_set: %s test_set:%s" %(control_set, test_set) )

    def addTestMembers(self, howmany=3):
        ### code that could be improved

        email = 'bobby@bobby.com'
        def gen_md(ints, data):
            for x in range(ints):
                fullname, email = data.next()
                yield ('%smember' %x, fullname, email)
                
        def gen_x(xs):
            for x in xs:
                yield x; 

        md = gen_md(howmany, gen_x( [(x, email) for x in fullnames] ))
        addM = self.portal.portal_membership.addMember
        
        out = "Creating %s Members" %howmany
        
        for id, fullname, email in md:
            out += "Create member:%s %s %s" %(id, fullname, email)
            addM(id, id, roles=('Member',), domains=[], properties={'fullname':fullname, 'email':email})
            
        return out

if __name__ == '__main__':
    framework(verbosity=1)
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestMemberSearch))
        return suite
