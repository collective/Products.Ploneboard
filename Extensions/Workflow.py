from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC
from Products.DCWorkflow.Default import p_request, p_review
from Products import CMFMember

# Execute the 'trigger' transition -- this should trigger
# any automatic transitions for which the guard conditions
# are satisfied.
def triggerAutomaticTransitions(ob):
    wf_tool=getToolByName(ob, 'portal_workflow')
    wf_tool.doActionFor(ob, 'trigger')

def setupWorkflow(portal, out):
    wf_tool=portal.portal_workflow

    if 'member_workflow' in wf_tool.objectIds():
        return

    wf_tool.manage_addWorkflow('dc_workflow (Web-configurable workflow)', 'member_workflow')

    wf = wf_tool['member_workflow']
    wf.setProperties(title='Portal Member Workflow')

    for s in ('new', 'pending', 'private', 'public'):
        wf.states.addState(s)
    wf.states.setInitialState('new')

    for t in ('trigger', 'auto_pending', 'auto_register', 'register_public', 'register_private', 'make_private', 'make_public'):
        wf.transitions.addTransition(t)

    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)

    if not hasattr(wf.scripts, 'register'):
        wf.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod('register', 'Register a Member', 'CMFMember.Install', 'register')

    perms = {}
    for p in (CMFMember.REGISTER_PERMISSION,
              CMFMember.EDIT_ID_PERMISSION,
              CMFMember.EDIT_REGISTRATION_PERMISSION,
              CMFMember.EDIT_PASSWORD_PERMISSION,
              CMFMember.EDIT_SECURITY_PERMISSION,
              CMFMember.EDIT_OTHER_PERMISSION,
              CMFMember.VIEW_SECURITY_PERMISSION,
              CMFMember.VIEW_PUBLIC_PERMISSION,
              CMFMember.VIEW_OTHER_PERMISSION,
              CMFMember.VIEW_PERMISSION):
        if not perms.has_key(p):
            wf.addManagedPermission(p)
            perms[p] = 1
    
    for l in ('reviewer_queue','member_queue'):
        wf.worklists.addWorklist(l)

    # STATES

    # New
    state = wf.states['new']
    state.setProperties(
        title='Newly created member',
        transitions=('trigger', 'auto_pending',))
    state.setPermission(CMFMember.REGISTER_PERMISSION, 0, ('Manager',))  # make anonymous to allow people to self-register
    state.setPermission(CMFMember.EDIT_ID_PERMISSION, 0, ('Anonymous',))
    state.setPermission(CMFMember.EDIT_REGISTRATION_PERMISSION, 0, ('Anonymous',))
    state.setPermission(CMFMember.EDIT_PASSWORD_PERMISSION, 0, ('Manager',)) # make anonymous to allow people to set their own initial passwords
    state.setPermission(CMFMember.EDIT_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.EDIT_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_PUBLIC_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.MAIL_PASSWORD_PERMISSION, 0, ('Manager',))

    # Pending approval
    state = wf.states['pending']
    state.setProperties(
        title='Awaiting registration',
        transitions=('trigger', 'auto_register', 'register_public', 'register_private',))
    state.setPermission(CMFMember.REGISTER_PERMISSION, 0, ('Manager',))  # make anonymous to allow people to self-register
    state.setPermission(CMFMember.EDIT_ID_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.EDIT_REGISTRATION_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.EDIT_PASSWORD_PERMISSION, 0, ('Manager',)) # make anonymous to allow people to set their own initial passwords
    state.setPermission(CMFMember.EDIT_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.EDIT_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_PUBLIC_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_OTHER_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.MAIL_PASSWORD_PERMISSION, 0, ('Manager',))

    # Registered, private
    state = wf.states['private']
    state.setProperties(
        title='Registered user, private profile',
        transitions=('trigger', 'make_public',))
    state.setPermission(CMFMember.REGISTER_PERMISSION, 0, ())
    state.setPermission(CMFMember.EDIT_ID_PERMISSION, 0, ())
    state.setPermission(CMFMember.EDIT_REGISTRATION_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(CMFMember.EDIT_PASSWORD_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(CMFMember.EDIT_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.EDIT_OTHER_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(CMFMember.VIEW_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_PUBLIC_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(CMFMember.VIEW_OTHER_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(CMFMember.VIEW_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.MAIL_PASSWORD_PERMISSION, 0, ('Anonymous', 'Authenticated'))

    # Registered, public
    state = wf.states['public']
    state.setProperties(
        title='Registered user, public profile',
        transitions=('trigger', 'make_private',))
    state.setPermission(CMFMember.REGISTER_PERMISSION, 0, ())
    state.setPermission(CMFMember.EDIT_ID_PERMISSION, 0, ())
    state.setPermission(CMFMember.EDIT_PASSWORD_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(CMFMember.EDIT_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.EDIT_OTHER_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(CMFMember.VIEW_SECURITY_PERMISSION, 0, ('Manager',))
    state.setPermission(CMFMember.VIEW_PUBLIC_PERMISSION, 0, ('Authenticated', 'Owner', 'Manager')) # allow Anonymous to let everyone view member info
    state.setPermission(CMFMember.VIEW_OTHER_PERMISSION, 0, ('Owner', 'Manager'))
    state.setPermission(CMFMember.VIEW_PERMISSION, 0, ('Authenticated', 'Manager')) # allow Anonymous to let everyone search for public members
    state.setPermission(CMFMember.MAIL_PASSWORD_PERMISSION, 0, ('Anonymous', 'Authenticated'))
    
    # TRANSITIONS

    # dummy transition used to trigger automatic transitions    
    transition = wf.transitions['trigger']
    transition.setProperties(
        title='Trigger automatic transitions',
        new_state_id='', # remain in state
        props={} # no guard roles or expressions
    ) 

    # change permissions as soon as user fills in member info
    transition = wf.transitions['auto_pending']
    transition.setProperties(
        title='Lock member properties until registered',
        new_state_id='pending',
        props={'trigger_type':TRIGGER_AUTOMATIC})

    # if Manager creates a member, automatically register the member
    transition = wf.transitions['auto_register']
    transition.setProperties(
        title='Make member profile public',
        new_state_id='public',
        props={'guard_roles':'Manager',
               'trigger_type':TRIGGER_AUTOMATIC
               }) #trigger_type=TRIGGER_AUTOMATIC})

    # manual registration
    transition = wf.transitions['register_private']
    transition.setProperties(
        title='Approve member, make profile private',
        new_state_id='private',
        actbox_name='Register member and make profile private',
        actbox_url='%(content_url)s/do_review',
        props={'guard_roles':'Manager'})

    # manual registration
    transition = wf.transitions['register_public']
    transition.setProperties(
        title='Approve member, make profile public',
        new_state_id='public',
        actbox_name='Register member and make profile public',
        actbox_url='%(content_url)s/do_review',
        props={'guard_roles':'Manager'})

    # make profile public
    transition = wf.transitions['make_public']
    transition.setProperties(
        title='Make member profile public',
        new_state_id='public',
        actbox_name='Make member profile public',
        actbox_url='%(content_url)s/do_review',
        props={'guard_roles':'Owner; Manager'})
    
    # make profile private
    transition = wf.transitions['make_private']
    transition.setProperties(
        title='Make member profile private',
        new_state_id='private',
        actbox_name='Make member profile private',
        actbox_url='%(content_url)s/do_review',
        props={'guard_roles':'Owner; Manager'})
    

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


    # set up worklists
    worklist = wf.worklists['member_queue']
    worklist.setProperties(description='Members to approve',
                       actbox_name='Members (%(count)d)',
                       actbox_url='%(portal_url)s/member_search?review_state=pending',
                       props={'var_match_review_state':'pending',
                              'guard_roles':'Manager'})


    wf_tool.setChainForPortalTypes((CMFMember.TYPE_NAME,), 'member_workflow')
    
    wf_tool.updateRoleMappings()
