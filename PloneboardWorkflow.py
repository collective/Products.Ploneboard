import os
from Globals import package_home

from Products.Ploneboard.config import GLOBALS
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Default import setupDefaultWorkflowRev2
from PloneboardPermissions import ViewBoard, SearchBoard, \
     ManageBoard, AddForum, ManageForum, AddConversation, AddComment, \
     EditComment, AddAttachment, ManageConversation, ManageComment, \
     ApproveComment
from AccessControl.Permissions import view, access_contents_information
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC
from Products.PythonScripts.PythonScript import manage_addPythonScript


# path_prefix is used for finding workflow scripts
path_prefix = os.path.join( package_home(GLOBALS)
                          , 'workflow_scripts')
# Default is to add all scripts for all workflows
# Override by defining script_ids as a tuple for each workflow
script_ids = [x[:-3] for x in filter(lambda y: y.endswith('.py'), os.listdir(path_prefix))]

p_access = access_contents_information
p_manage = ManageForum
p_modify = EditComment
p_view = ViewBoard
p_review = ApproveComment
p_request = AddConversation
p_reply = AddComment

r_anon = 'Anonymous'
r_manager = 'Manager'
r_reviewer = 'Reviewer'
r_owner = 'Owner'
r_member = 'Member'

def setupPloneboardCommentWorkflow(wf):
    """ Sets up a workflow for Ploneboard Comments """
    wf.setProperties(title='Ploneboard Comment Workflow [Ploneboard]')

    for s in ('initial', 'pending', 'published', 'rejected', 'locked'):
        wf.states.addState(s)
    for t in ('publish', 'reject', 'submit', 'autosubmit', 'autopublish', 'lock'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for script_id in script_ids:
        manage_addPythonScript(wf.scripts, script_id)
        scr = getattr(wf.scripts, script_id)
        scr.write(open(os.path.join(path_prefix, '%s.py' % script_id)).read())
    for l in ('reviewer_queue', 'submitter_queue'):
        wf.worklists.addWorklist(l)
    for p in (p_access, p_view, p_modify, p_request, p_reply):
        wf.addManagedPermission(p)

    wf.states.setInitialState('initial')

    #******* Set up workflow states *******
    sdef = wf.states['initial']
    sdef.setProperties(
        title='Initial state',
        transitions=('autosubmit', 'autopublish',))
    sdef.setPermission(p_access,  0, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_view,    0, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_modify,  0, (r_manager, r_reviewer))
    sdef.setPermission(p_request, 0, (r_manager, r_owner))
    sdef.setPermission(p_reply,   0, (r_manager,))

    sdef = wf.states['pending']
    sdef.setProperties(
        title='Waiting for reviewer',
        transitions=('publish', 'reject', 'lock',))
    sdef.setPermission(p_access,  0, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_view,    0, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_modify,  0, (r_manager, r_reviewer))
    sdef.setPermission(p_request, 0, (r_manager, r_owner))
    sdef.setPermission(p_reply,   0, (r_manager,))

    sdef = wf.states['published']
    sdef.setProperties(
        title='Public',
        transitions=('reject', 'lock', ))
    # Inherit from forum, enables private forums
    sdef.setPermission(p_access,  1, (r_manager,))
    sdef.setPermission(p_view,    1, (r_manager,))
    sdef.setPermission(p_modify,  0, (r_manager,))
    sdef.setPermission(p_request, 1, (r_manager,))
    sdef.setPermission(p_reply,   1, (r_manager,))
    
    sdef = wf.states['rejected']
    sdef.setProperties(
        title='Non-visible and editable only by owner',
        transitions=('submit', 'publish',))
    sdef.setPermission(p_access,  0, (r_manager, r_owner))
    sdef.setPermission(p_view,    0, (r_manager, r_owner))
    sdef.setPermission(p_modify,  0, (r_manager, r_owner))
    sdef.setPermission(p_request, 0, (r_manager,))
    sdef.setPermission(p_reply,   0, (r_manager,))

    sdef = wf.states['locked']
    sdef.setProperties(
        title='Locked',
        transitions=('publish', 'reject',))
    # Inherit from forum, enables private forums
    sdef.setPermission(p_access,  1, (r_manager,))
    sdef.setPermission(p_view,    1, (r_manager,))
    sdef.setPermission(p_modify,  0, (r_manager,))
    sdef.setPermission(p_request, 0, (r_manager,))
    sdef.setPermission(p_reply,   0, (r_manager,))


    # ***** Set up transitions *****
    tdef = wf.transitions['publish']
    tdef.setProperties(
        title='Reviewer publishes content',
        new_state_id='published',
        # The publish_script is added to scripts folder by the Install script
        after_script_name='publish_script',
        actbox_name='Publish',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_review})

    tdef = wf.transitions['autopublish']
    tdef.setProperties(
        title='Automatic publishing in unmoderated boards',
        new_state_id='published',
        trigger_type=TRIGGER_AUTOMATIC,
        # The autopublish_script is added to scripts folder by the Install script
        after_script_name='autopublish_script',
        props={ 'guard_permissions':p_request
              , 'guard_expr':'not: here/isModerated'})

    tdef = wf.transitions['autosubmit']
    tdef.setProperties(
        title='Automatic submit in moderated boards',
        new_state_id='pending',
        trigger_type=TRIGGER_AUTOMATIC,
        # The autosubmit_script is added to scripts folder by the Install script
        after_script_name='autosubmit_script',
        props={ 'guard_permissions':p_request
              , 'guard_expr':'here/isModerated'})

    tdef = wf.transitions['reject']
    tdef.setProperties(
        title='Reviewer rejects submission',
        new_state_id='rejected',
        # The reject_script is added to scripts folder by the Install script
        after_script_name='reject_script',
        actbox_name='Reject',
        actbox_url='%(content_url)s/content_reject_form',
        props={'guard_permissions':p_review})

    tdef = wf.transitions['submit']
    tdef.setProperties(
        title='Member requests publishing',
        new_state_id='pending',
        # The submit_script is added to scripts folder by the Install script
        after_script_name='submit_script',
        actbox_name='Submit',
        actbox_url='%(content_url)s/content_submit_form',
        props={'guard_permissions':p_request})

    tdef = wf.transitions['lock']
    tdef.setProperties(
        title='Lock comment',
        new_state_id='locked',
        # The lock_script is added to scripts folder by the Install script
        after_script_name='lock_script',
        actbox_name='Lock',
        actbox_url='%(content_url)s/content_submit_form',
        props={'guard_permissions':p_review})

    wf.variables.setStateVar('review_state')

    # **** Setting up variables ****
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

    # ***** Setting up worklists *****
    ldef = wf.worklists['reviewer_queue']
    ldef.setProperties(description='Reviewer tasks',
                       actbox_name='Pending comments',
                       actbox_url='%(portal_url)s/search?review_state=pending',
                       props={'var_match_review_state':'pending',
                              'guard_permissions':p_review})

    ldef = wf.worklists['submitter_queue']
    ldef.setProperties(description='Submitter tasks',
                       actbox_name='Rejected comments',
                       actbox_url='%(portal_url)s/search?review_state=rejected',
                       props={'var_match_review_state':'rejected',
                              'guard_permissions':p_modify,
                              'guard_roles':r_owner})

def createPloneboardCommentWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupPloneboardCommentWorkflow(ob)
    ob.setProperties(title='Comment Workflow [Ploneboard]')
    return ob

addWorkflowFactory( createPloneboardCommentWorkflow, id='ploneboard_comment_workflow'
                  , title='Comment Workflow [Ploneboard]')	





def setupPloneboardForumWorkflow(wf):
    """ Sets up a workflow for Ploneboard Forums """
    wf.setProperties(title='Ploneboard Forum Workflow [Ploneboard]')

    for s in ('freeforall', 'memberposting', 'moderated', 'private'):
        wf.states.addState(s)
    for t in ('make_freeforall', 'make_memberposting', 'make_moderated', 'make_private'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for script_id in script_ids:
        manage_addPythonScript(wf.scripts, script_id)
        scr = getattr(wf.scripts, script_id)
        scr.write(open(os.path.join(path_prefix, '%s.py' % script_id)).read())
    for p in (p_access, p_view, p_request, p_reply):
        wf.addManagedPermission(p)

    wf.states.setInitialState('freeforall')

    #******* Set up workflow states *******
    sdef = wf.states['freeforall']
    sdef.setProperties(
        title='Free for all',
        transitions=('make_memberposting', 'make_moderated', 'make_private'))
    sdef.setPermission(p_access,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_view,    1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_request, 1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_reply,   1, (r_manager, r_anon, r_member))
    
    sdef = wf.states['memberposting']
    sdef.setProperties(
        title='Require membership to post',
        transitions=('make_freeforall', 'make_moderated', 'make_private'))
    sdef.setPermission(p_access,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_view,    1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_request, 0, (r_manager, r_member))
    sdef.setPermission(p_reply,   0, (r_manager, r_member))

    sdef = wf.states['moderated']
    sdef.setProperties(
        title='Moderated forum',
        transitions=('make_freeforall', 'make_memberposting', 'make_private'))
    sdef.setPermission(p_access,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_view,    1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_request, 1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_reply,   1, (r_manager, r_anon, r_member))

    sdef = wf.states['private']
    sdef.setProperties(
        title='Private to members only',
        transitions=('make_freeforall', 'make_memberposting', 'make_moderated'))
    sdef.setPermission(p_access,  0, (r_manager, r_member))
    sdef.setPermission(p_view,    0, (r_manager, r_member))
    sdef.setPermission(p_request, 0, (r_manager, r_member))
    sdef.setPermission(p_reply,   0, (r_manager, r_member))

    # ***** Set up transitions *****
    tdef = wf.transitions['make_freeforall']
    tdef.setProperties(
        title='Make the forum free for all',
        new_state_id='freeforall',
        # The publish_script is added to scripts folder by the Install script
        after_script_name='make_unmoderated_script',
        actbox_name='Freeforall',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_manage})

    tdef = wf.transitions['make_memberposting']
    tdef.setProperties(
        title='Only let members post',
        new_state_id='memberposting',
        # The make_unmoderated_script is added to scripts folder by the Install script
        after_script_name='make_unmoderated_script',
        actbox_name='Memberposting',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_manage})

    tdef = wf.transitions['make_moderated']
    tdef.setProperties(
        title='Make moderated',
        new_state_id='moderated',
        # The make_moderated_script is added to scripts folder by the Install script
        after_script_name='make_moderated_script',
        actbox_name='Moderated',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_manage})

    tdef = wf.transitions['make_private']
    tdef.setProperties(
        title='Private closed board',
        new_state_id='private',
        # The make_unmoderated_script is added to scripts folder by the Install script
        after_script_name='make_unmoderated_script',
        actbox_name='Private',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_manage})

    wf.variables.setStateVar('review_state')

    # **** Setting up variables ****
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

def createPloneboardForumWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupPloneboardForumWorkflow(ob)
    ob.setProperties(title='Forum Workflow [Ploneboard]')
    return ob

addWorkflowFactory( createPloneboardForumWorkflow, id='ploneboard_forum_workflow'
                  , title='Forum Workflow [Ploneboard]')


def setupPloneboardWorkflow(wf):
    """ Sets up a workflow for Ploneboards """
    # The important thing is to add the ploneboard permissions to the workflow
    setupDefaultWorkflowRev2(wf)
    wf.setProperties(title='Ploneboard Workflow [Ploneboard]')

    for p in (ViewBoard, SearchBoard, ManageBoard, ManageForum, 
              AddConversation, AddComment, EditComment, AddAttachment, 
              ManageConversation, ManageComment, ApproveComment):
        wf.addManagedPermission(p)

    sdef = wf.states['private']
    sdef.setPermission(ViewBoard,          0, (r_manager, r_owner))
    sdef.setPermission(SearchBoard,        0, (r_manager, r_owner))
    sdef.setPermission(ManageBoard,        0, (r_manager, r_owner))
    sdef.setPermission(ManageForum,        0, (r_manager, r_owner))
    sdef.setPermission(AddConversation,    0, (r_manager, r_owner))
    sdef.setPermission(AddComment,         0, (r_manager, r_owner))
    sdef.setPermission(EditComment,        0, (r_manager, r_owner))
    sdef.setPermission(AddAttachment,      0, (r_manager, r_owner))
    sdef.setPermission(ManageConversation, 0, (r_manager, r_owner))
    sdef.setPermission(ManageComment,      0, (r_manager, r_owner))
    sdef.setPermission(ApproveComment,     0, (r_manager, r_owner))

    sdef = wf.states['pending']
    sdef.setPermission(ViewBoard,          1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(SearchBoard,        1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(ManageBoard,        0, (r_manager, r_reviewer))
    sdef.setPermission(ManageForum,        0, (r_manager, r_reviewer))
    sdef.setPermission(AddConversation,    0, (r_manager, r_reviewer))
    sdef.setPermission(AddComment,         0, (r_manager, r_reviewer))
    sdef.setPermission(EditComment,        0, (r_manager, r_reviewer))
    sdef.setPermission(AddAttachment,      0, (r_manager, r_reviewer))
    sdef.setPermission(ManageConversation, 0, (r_manager, r_reviewer))
    sdef.setPermission(ManageComment,      0, (r_manager, r_reviewer))
    sdef.setPermission(ApproveComment,     0, (r_manager, r_reviewer))

    sdef = wf.states['published']
    sdef.setPermission(ViewBoard,          1, (r_anon, r_manager))
    sdef.setPermission(SearchBoard,        1, (r_anon, r_manager))
    sdef.setPermission(ManageBoard,        0, (r_manager,))
    sdef.setPermission(ManageForum,        0, (r_manager,))
    sdef.setPermission(AddConversation,    0, (r_manager,))
    sdef.setPermission(AddComment,         0, (r_manager,))
    sdef.setPermission(EditComment,        0, (r_manager,))
    sdef.setPermission(AddAttachment,      0, (r_manager,))
    sdef.setPermission(ManageConversation, 0, (r_manager,))
    sdef.setPermission(ManageComment,      0, (r_manager,))
    sdef.setPermission(ApproveComment,     0, (r_manager,))

    sdef = wf.states['visible']
    sdef.setPermission(ViewBoard,          1, (r_anon, r_manager, r_reviewer))
    sdef.setPermission(SearchBoard,        1, (r_anon, r_manager, r_reviewer))
    sdef.setPermission(ManageBoard,        0, (r_manager, r_owner))
    sdef.setPermission(ManageForum,        0, (r_manager, r_owner))
    sdef.setPermission(AddConversation,    0, (r_manager, r_owner))
    sdef.setPermission(AddComment,         0, (r_manager, r_owner))
    sdef.setPermission(EditComment,        0, (r_manager, r_owner))
    sdef.setPermission(AddAttachment,      0, (r_manager, r_owner))
    sdef.setPermission(ManageConversation, 0, (r_manager, r_owner))
    sdef.setPermission(ManageComment,      0, (r_manager, r_owner))
    sdef.setPermission(ApproveComment,     0, (r_manager, r_owner))

def createPloneboardWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupPloneboardWorkflow(ob)
    ob.setProperties(title='Ploneboard Workflow [Ploneboard]')
    return ob

addWorkflowFactory( createPloneboardWorkflow, id='ploneboard_workflow'
                  , title='Ploneboard Workflow [Ploneboard]')

