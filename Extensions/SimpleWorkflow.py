from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC, TRIGGER_WORKFLOW_METHOD
from Products.DCWorkflow.Default import p_request, p_review
from Products import CMFMember
from Products.CMFMember import MemberPermissions
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.WorkflowTool import addWorkflowFactory


wf_id='simple_member_workflow'

# Execute the 'trigger' transition -- this should trigger
# any automatic transitions for which the guard conditions
# are satisfied.
def triggerAutomaticTransitions(ob):
    wf_tool=getToolByName(ob, 'portal_workflow')
    if 'trigger' in [action.get('id',None) for action in wf_tool.getActionsFor(ob)]:
        wf_tool.doActionFor(ob, 'trigger')

def setupWorkflow(portal, out):
    wf_tool=portal.portal_workflow

    if wf_id in wf_tool.objectIds():
        return

    wf_tool.manage_addWorkflow('dc_workflow (Web-configurable workflow)', 
                               wf_id)

    wf = wf_tool['simple_member_workflow']
    wf.setProperties(title='Simple Member Workflow')

    wf.states.addState('registered')
    wf.states.setInitialState('registered')

    perms = {}
    for p in (MemberPermissions.REGISTER_PERMISSION,
              MemberPermissions.EDIT_ID_PERMISSION,
              MemberPermissions.EDIT_PROPERTIES_PERMISSION,
              MemberPermissions.EDIT_PASSWORD_PERMISSION,
              MemberPermissions.EDIT_SECURITY_PERMISSION,
              MemberPermissions.VIEW_SECURITY_PERMISSION,
              MemberPermissions.VIEW_PUBLIC_PERMISSION,
              MemberPermissions.VIEW_OTHER_PERMISSION,
              MemberPermissions.VIEW_PERMISSION,
              CMFCorePermissions.ModifyPortalContent):
        if not perms.has_key(p):
            wf.addManagedPermission(p)
            perms[p] = 1
    
    # New
    state = wf.states['registered']

    state.setProperties( title='Registered user, public profile',
                         transitions=() )

    state.setPermission(MemberPermissions.REGISTER_PERMISSION, 0, ())
    state.setPermission(MemberPermissions.EDIT_ID_PERMISSION, 0, ())
    state.setPermission(MemberPermissions.EDIT_PASSWORD_PERMISSION, 0, 
                        ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.EDIT_SECURITY_PERMISSION, 0, 
                        ('Manager',))
    state.setPermission(MemberPermissions.EDIT_PROPERTIES_PERMISSION, 0, 
                        ('Owner', 'Manager',))
    state.setPermission(MemberPermissions.VIEW_SECURITY_PERMISSION, 0, 
                        ('Manager',))
    # allow Anonymous to let everyone view member info
    state.setPermission(MemberPermissions.VIEW_PUBLIC_PERMISSION, 0, 
                        ('Authenticated', 'Owner', 'Manager')) 
    state.setPermission(MemberPermissions.VIEW_OTHER_PERMISSION, 0, 
                        ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.VIEW_PERMISSION, 0,
                        ('Authenticated', 'Manager')) 
    # allow Anonymous to let everyone search for public members
    state.setPermission(MemberPermissions.MAIL_PASSWORD_PERMISSION, 0, 
                        ('Anonymous', 'Authenticated'))
    state.setPermission(CMFCorePermissions.ModifyPortalContent, 0, 
                        ('Owner', 'Manager',))
    
    wf_tool.updateRoleMappings()

def createSimpleMemberWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupPrivatePloneWorkflow(ob)
    configureEventPermissions(ob)
    ob.setProperties(title='Private Workflow [Plone]')
    return ob

addWorkflowFactory( createSimpleMemberWorkflow,
                    id='private_plone_workflow',
                    title='Private Workflow [Plone]' )


