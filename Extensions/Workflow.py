from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC, TRIGGER_WORKFLOW_METHOD
from Products.DCWorkflow.Default import p_request, p_review
from Products import CMFMember
from Products.CMFMember import MemberPermissions
from Products.CMFCore import CMFCorePermissions
from Products.CMFMember.Extensions import MemberApprovalWorkflow
from Products.CMFMember.Extensions import MemberAutoWorkflow

# Execute the 'trigger' transition -- this should trigger
# any automatic transitions for which the guard conditions
# are satisfied.
def triggerAutomaticTransitions(ob):
    wf_tool=getToolByName(ob, 'portal_workflow')
    if 'trigger' in [action.get('id',None) for action in wf_tool.getActionsFor(ob)]:
        wf_tool.doActionFor(ob, 'trigger')


def addWorkflowScripts(wf):
    if not 'register' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('register', 'Register a Member', 'CMFMember.Workflow', 'register')
    if not 'autoRegister' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('autoRegister', 'Auto-Register a Member', 'CMFMember.Workflow', 'autoRegister')
    if not 'disable' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('disable', 'Disable a Member', 'CMFMember.Workflow', 'disable')
    if not 'enable' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('enable', 'Enable a Member', 'CMFMember.Workflow', 'enable')
    if not 'makePublic' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('makePublic', 'Make a Member profile public', 'CMFMember.Workflow', 'makePublic')
    if not 'makePrivate' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('makePrivate', 'Make a Member profile private', 'CMFMember.Workflow', 'makePrivate')
    if not 'enable' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('enable', 'Make a Member profile private', 'CMFMember.Workflow', 'makePrivate')
    

def setupWorkflow(portal, out):
    wf_tool=portal.portal_workflow

    if not 'member_approval_workflow' in wf_tool.objectIds():
        wf_tool.manage_addWorkflow('member_approval_workflow (Portal Member Workflow: Approval Required)',
                                   'member_approval_workflow')
        addWorkflowScripts(wf_tool['member_approval_workflow'])

    if not 'member_auto_workflow' in wf_tool.objectIds():
        wf_tool.manage_addWorkflow('member_auto_workflow (Portal Member Workflow: Automatic Approval)',
                                   'member_auto_workflow')
        addWorkflowScripts(wf_tool['member_auto_workflow'])

    wf_tool.updateRoleMappings()

# Transitions that need to be executed in order to move to a particular
# workflow state
workflow_transfer = {'new': [],
                     'pending': ['trigger'],
                     'registered_public':['migrate'],
                     'registered_private':['migrate', 'make_private'],
                     'disabled':['trigger', 'disable']
                    }


# call the Member object's register() method
def register(self, state_change):
    obj=state_change.object
    return obj.register()

# call the Member object's autoRegister() method
def autoRegister(self, state_change):
    obj=state_change.object
    return obj.autoRegister()

# call the Member object's disable() method
def disable(self, state_change):
    obj=state_change.object
    return obj.disable()


# call the Member object's enable() method
def enable(self, state_change):
    obj=state_change.object
    return obj.enable()


def makePublic(self, state_change):
    obj=state_change.object
    return obj.makePublic()


def makePrivate(self, state_change):
    obj=state_change.object
    return obj.makePrivate()
