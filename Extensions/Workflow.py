from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC, TRIGGER_WORKFLOW_METHOD
from Products.DCWorkflow.Default import p_request, p_review
from Products import CMFMember
from Products.CMFMember import MemberPermissions
from Products.CMFCore import CMFCorePermissions

# Execute the 'trigger' transition -- this should trigger
# any automatic transitions for which the guard conditions
# are satisfied.
def triggerAutomaticTransitions(ob):
    wf_tool=getToolByName(ob, 'portal_workflow')
    if 'trigger' in [action.get('id',None) for action in wf_tool.getActionsFor(ob)]:
        wf_tool.doActionFor(ob, 'trigger')


def setupWorkflow(portal, out):
    wf_tool=portal.portal_workflow

    if 'member_workflow' in wf_tool.objectIds():
        return

    wf_tool.manage_addWorkflow('dc_workflow (Web-configurable workflow)', 'member_workflow')

    wf = wf_tool['member_workflow']
    wf.setProperties(title='Portal Member Workflow')

    for s in ('new', 'pending', 'private', 'public', 'disabled'):
        wf.states.addState(s)
    wf.states.setInitialState('new')

    for t in ('trigger', 'make_pending', 'auto_register',
              'register_public', 'register_private',
              'make_private', 'make_public',
              'disable', 'enable_pending', 'enable_public', 'enable_private',
              'migrate'):
        wf.transitions.addTransition(t)

    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)

    if not 'register' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('register', 'Register a Member', 'CMFMember.Workflow', 'register')
    if not 'disable' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('disable', 'Disable a Member', 'CMFMember.Workflow', 'disable')
    if not 'enable' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('enable', 'Enable a Member', 'CMFMember.Workflow', 'enable')
    if not 'makePublic' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('makePublic', 'Make a Member profile public', 'CMFMember.Workflow', 'makePublic')
    if not 'enable' in wf.scripts.objectIds():
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('enable', 'Make a Member profile private', 'CMFMember.Workflow', 'makePrivate')

    perms = {}
    for p in (MemberPermissions.REGISTER_PERMISSION,
              MemberPermissions.EDIT_ID_PERMISSION,
              MemberPermissions.EDIT_REGISTRATION_PERMISSION,
              MemberPermissions.EDIT_PASSWORD_PERMISSION,
              MemberPermissions.EDIT_SECURITY_PERMISSION,
              MemberPermissions.EDIT_OTHER_PERMISSION,
              MemberPermissions.VIEW_SECURITY_PERMISSION,
              MemberPermissions.VIEW_PUBLIC_PERMISSION,
              MemberPermissions.VIEW_OTHER_PERMISSION,
              MemberPermissions.VIEW_PERMISSION,
              CMFCorePermissions.ModifyPortalContent):
        if not perms.has_key(p):
            wf.addManagedPermission(p)
            perms[p] = 1
    
    for l in ('reviewer_queue',):
        wf.worklists.addWorklist(l)

    # STATES

    # New
    state = wf.states['new']
    state.setProperties(
        title='Newly created member',
        transitions=('trigger', 'make_pending', 'migrate'))
    state.setPermission(MemberPermissions.REGISTER_PERMISSION, 0, ('Manager',))  # make anonymous to allow people to self-register
    state.setPermission(MemberPermissions.EDIT_ID_PERMISSION, 0, ('Manager','Anonymous',))
    state.setPermission(MemberPermissions.EDIT_REGISTRATION_PERMISSION, 0, ('Manager','Anonymous',))
    state.setPermission(MemberPermissions.EDIT_PASSWORD_PERMISSION, 0, ('Manager',)) # make anonymous to allow people to set their own initial passwords
    state.setPermission(MemberPermissions.EDIT_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_PUBLIC_PERMISSION, 0, ('Manager','Anonymous',))
    state.setPermission(MemberPermissions.VIEW_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_PERMISSION, 0, ('Manager','Anonymous'))
    state.setPermission(MemberPermissions.MAIL_PASSWORD_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFCorePermissions.ModifyPortalContent, 0, ('Anonymous',))

    # Pending approval
    state = wf.states['pending']
    state.setProperties(
        title='Awaiting registration',
        transitions=('register_public', 'register_private', 'disable',))
    state.setPermission(MemberPermissions.REGISTER_PERMISSION, 0, ('Manager',))  # make anonymous to allow people to self-register
    state.setPermission(MemberPermissions.EDIT_ID_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_REGISTRATION_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_PASSWORD_PERMISSION, 0, ('Manager',)) # make anonymous to allow people to set their own initial passwords
    state.setPermission(MemberPermissions.EDIT_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_PUBLIC_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.MAIL_PASSWORD_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFCorePermissions.ModifyPortalContent, 0, ('Manager',))

    # Registered, private
    state = wf.states['private']
    state.setProperties(
        title='Registered user, private profile',
        transitions=('make_public','disable',))
    state.setPermission(MemberPermissions.REGISTER_PERMISSION, 0, ())
    state.setPermission(MemberPermissions.EDIT_ID_PERMISSION, 0, ())
    state.setPermission(MemberPermissions.EDIT_REGISTRATION_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.EDIT_PASSWORD_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.EDIT_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_OTHER_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.VIEW_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_PUBLIC_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.VIEW_OTHER_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.VIEW_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.MAIL_PASSWORD_PERMISSION, 0, ('Anonymous', 'Authenticated'))
    state.setPermission(CMFCorePermissions.ModifyPortalContent, 0, ('Owner', 'Manager',))

    # Registered, public
    state = wf.states['public']
    state.setProperties(
        title='Registered user, public profile',
        transitions=('make_private','disable',))
    state.setPermission(MemberPermissions.REGISTER_PERMISSION, 0, ())
    state.setPermission(MemberPermissions.EDIT_ID_PERMISSION, 0, ())
    state.setPermission(MemberPermissions.EDIT_REGISTRATION_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.EDIT_PASSWORD_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.EDIT_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_OTHER_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.VIEW_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_PUBLIC_PERMISSION, 0, ('Authenticated', 'Owner', 'Manager')) # allow Anonymous to let everyone view member info
    state.setPermission(MemberPermissions.VIEW_OTHER_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(MemberPermissions.VIEW_PERMISSION, 0, ('Authenticated', 'Manager')) # allow Anonymous to let everyone search for public members
    state.setPermission(MemberPermissions.MAIL_PASSWORD_PERMISSION, 0, ('Anonymous', 'Authenticated'))
    state.setPermission(CMFCorePermissions.ModifyPortalContent, 0, ('Owner', 'Manager',))
    
    # Disabled
    state = wf.states['disabled']
    state.setProperties(
        title='Disabled',
        transitions=('enable_pending', 'enable_private', 'enable_public',))
    state.setPermission(MemberPermissions.REGISTER_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_ID_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_REGISTRATION_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_PASSWORD_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.EDIT_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_PUBLIC_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.VIEW_PERMISSION, 0, ('Manager',))
    state.setPermission(MemberPermissions.MAIL_PASSWORD_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFCorePermissions.ModifyPortalContent, 0, ('Manager',))

    # TRANSITIONS

    # registration for migration -- don't execute the register script
    transition = wf.transitions['migrate']
    transition.setProperties(
        title='Migrate member from CMF MemberData',
        actbox_name='Migrate member from CMF MemberData',
        new_state_id='public',
        props={'guard_roles':'Manager'},
        after_script_name='makePublic')

    # dummy transition used to trigger automatic transitions    
    transition = wf.transitions['trigger']
    transition.setProperties(
        title='Trigger automatic transitions',
        actbox_name='Trigger automatic transitions',
        new_state_id='', # remain in state
        props={}, # no guard roles or expressions
    ) 

    # change permissions as soon as user fills in required member info
    # (or before if the user already exists in another acl_users)
    transition = wf.transitions['make_pending']
    transition.setProperties(
        title='Lock member properties until registered',
        actbox_name='Lock member properties until registered',
        new_state_id='pending',
        trigger_type=TRIGGER_AUTOMATIC,
        props={'guard_expr':'python:here.hasUser() or here.isValid()'})

    # if Manager creates a member, automatically register the member
    transition = wf.transitions['auto_register']
    transition.setProperties(
        title='Automatically approve member',
        actbox_name='Automatically approve member',
        new_state_id='public',
        trigger_type=TRIGGER_AUTOMATIC,
        props={'guard_permissions':MemberPermissions.REGISTER_PERMISSION,
               'guard_expr':'here/isValid'},
        after_script_name='register')

    # manual registration
    transition = wf.transitions['register_private']
    transition.setProperties(
        title='Approve member, make profile private',
        actbox_name='Register member and make profile private',
        new_state_id='private',
        props={'guard_permissions':MemberPermissions.REGISTER_PERMISSION,
               'guard_expr':'here/isValid'},
        after_script_name='register')

    # manual registration
    transition = wf.transitions['register_public']
    transition.setProperties(
        title='Approve member, make profile public',
        actbox_name='Register member and make profile public',
        new_state_id='public',
        props={'guard_permissions':MemberPermissions.REGISTER_PERMISSION,
               'guard_expr':'here/isValid'},
        after_script_name='register')

    # make profile public
    transition = wf.transitions['make_public']
    transition.setProperties(
        title='Make member profile public',
        actbox_name='Make member profile public',
        new_state_id='public',
        props={'guard_roles':'Owner; Manager'},
        after_script_name='makePublic')
    
    # make profile private
    transition = wf.transitions['make_private']
    transition.setProperties(
        title='Make member profile private',
        actbox_name='Make member profile private',
        new_state_id='private',
        props={'guard_roles':'Owner; Manager'},
        after_script_name='makePrivate')

    # disable member
    transition = wf.transitions['disable']
    transition.setProperties(
        title='Disable member',
        actbox_name='Disable member',
        new_state_id='disabled',
        props={'guard_permissions':MemberPermissions.DISABLE_PERMISSION,},
        script_name='disable')

    # re-enable disabled member
    transition = wf.transitions['enable_pending']
    transition.setProperties(
        title='Re-enable member',
        actbox_name='Re-enable member',
        new_state_id='pending',
        props={'guard_permissions':MemberPermissions.DISABLE_PERMISSION,
               'guard_expr':'python:getattr(here,\'old_state\',None) == \'pending\''},
        after_script_name='enable')

    # re-enable disabled member
    transition = wf.transitions['enable_public']
    transition.setProperties(
        title='Re-enable member',
        actbox_name='Re-enable member',
        new_state_id='public',
        props={'guard_permissions':MemberPermissions.DISABLE_PERMISSION,
               'guard_expr':'python:getattr(here,\'old_state\',None) == \'public\''},
        after_script_name='enable')

    # re-enable disabled member
    transition = wf.transitions['enable_private']
    transition.setProperties(
        title='Re-enable member',
        actbox_name='Re-enable member',
        new_state_id='private',
        props={'guard_permissions':MemberPermissions.DISABLE_PERMISSION,
               'guard_expr':'python:getattr(here,\'old_state\',None) == \'private\''},
        after_script_name='enable')
    
    # standard CMF variables so we can use content_status_history page, etc
    wf.variables.setStateVar('review_state')

    vdef = wf.variables['action']
    vdef.setProperties(description='The last transition',
                       default_expr='transition/getId|nothing',
                       for_status=1, update_always=1)

    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed '
                       'the last transition',
                       default_expr='user/getId',
                       for_status=1, update_always=1)

    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_expr="python:state_change.kwargs.get('comment', '')",
                       for_status=1, update_always=1)

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_expr="state_change/getHistory",
                       props={'guard_permissions':
                              p_request + ';' + p_review})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

    ldef = wf.worklists['reviewer_queue']
    ldef.setProperties(description='Reviewer tasks',
                       actbox_name='Pending (%(count)d)',
                       actbox_url='%(portal_url)s/search?review_state=pending',
                       props={'var_match_review_state':'pending',
                              'guard_permissions':p_review})

    wf_tool.updateRoleMappings()

# Transitions that need to be executed in order to move to a particular
# workflow state
workflow_transfer = {'new': [],
                     'pending': ['trigger'],
                     'registered_public':['trigger', 'register_public'],
                     'registered_private':['trigger', 'register_private'],
                     'disabled':['trigger', 'register_private', 'disable']
                    }


# call the Member object's register() method
def register(self, state_change):
    obj=state_change.object
    return obj.register()


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
