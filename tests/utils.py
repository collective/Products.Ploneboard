from zope.app.tests import placelesssetup

from Products.Five import zcml
import Products.Five
import Products.ATContentTypes

from DateTime import DateTime

def addMember(self, username, fullname="", email="", roles=('Member',), last_login_time=None):
    self.portal.portal_membership.addMember(username, 'secret', roles, [])
    member = self.portal.portal_membership.getMemberById(username)
    member.setMemberProperties({'fullname': fullname, 'email': email,
                                'last_login_time': DateTime(last_login_time),})

def setUpDefaulMembersBoardAndForum(self):
    addMember(self, 'member1', 'Member one', roles=('Member',))
    addMember(self, 'member2', 'Member two', roles=('Member',))
    addMember(self, 'manager1', 'Manager one', roles=('Manager',))
    addMember(self, 'reviewer1', 'Manager one', roles=('Reviewer',))
    
    self.workflow = self.portal.portal_workflow
    
    self.setRoles(('Manager',))
    self.portal.invokeFactory('Ploneboard', 'board1')
    self.board = self.portal.board1
    self.forum = self.board.addForum('forum1', 'Forum 1', 'Forum one')
    self.setRoles(('Member',))

def disableScriptValidators(portal):
    from Products.CMFFormController.FormController import ANY_CONTEXT, ANY_BUTTON
    scripts = ['add_comment_script', 'add_conversation_script', 'add_forum_script']
    try:
        for v in portal.portal_skins.ploneboard_scripts.objectValues():
            if v.id in scripts:
                v.manage_doCustomize('custom')
                portal.portal_form_controller.addFormValidators(v.id, ANY_CONTEXT, ANY_BUTTON, [])
    except:
        pass

def caSetUp(self):
    """Setup component architecture"""
    
    # some nasty Five bug in old Five versions needs _context reset
    Products.Five.zcml._context = None
    
    placelesssetup.setUp()
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('permissions.zcml', Products.Five)
    try:
        zcml.load_config('bridge.zcml', Products.ATContentTypes)
    except IOError:
        # In Plone 2.5 and up, this file doesn't exist
        pass
    zcml.load_config('configure.zcml', Products.Ploneboard)

    # in some circumstances tests get run in a strange order which
    # messes up Five's traversal logic

    zcml.load_string('''<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:five="http://namespaces.zope.org/five">
  <!-- basic collection of directives needed for proper traversal and request handling -->
  <include package="zope.app.traversing" />
  <adapter
      for="*"
      factory="Products.Five.traversable.FiveTraversable"
      provides="zope.app.traversing.interfaces.ITraversable"
      />
  <adapter
      for="*"
      factory="zope.app.traversing.adapters.Traverser"
      provides="zope.app.traversing.interfaces.ITraverser"
      />
  <five:implements class="ZPublisher.HTTPRequest.HTTPRequest"
                   interface="zope.publisher.interfaces.browser.IBrowserRequest"
                   />

</configure>''')

def caTearDown(self):
    """Tear down component architecture"""

    # tests based on PloneTestCase incorrectly setup Five which means
    # proper cleanup can never take place ... so coomenting out the
    # placelesssetup.tearDown() call - Rocky
    
    #placelesssetup.tearDown()
