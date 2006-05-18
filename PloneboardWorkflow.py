import os
from Globals import package_home

from Products.Ploneboard.config import GLOBALS
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Default import setupDefaultWorkflowRev2
from permissions import ViewBoard, SearchBoard, ManageBoard, AddForum, ManageForum,\
     AddConversation, AddComment, EditComment, AddAttachment, ManageConversation,\
     ManageComment, ApproveComment, RequestReview
from AccessControl.Permissions import view, access_contents_information
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC
from Products.PythonScripts.PythonScript import manage_addPythonScript
from Products.CMFCore.permissions import AddPortalContent

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
p_addconv = AddConversation
p_addcomm = AddComment
p_manageconv = ManageConversation
p_requestreview = RequestReview
# Unfortunately, the method of registering our archetype-derived objects with different
# add permissions also means that the AddPortalContent permission is needed by users
# who want to add as well.
p_addpc = AddPortalContent

r_anon = 'Anonymous'
r_manager = 'Manager'
r_reviewer = 'Reviewer'
r_owner = 'Owner'
r_member = 'Member'

def setupPloneboardCommentWorkflow(wf):
    """ Sets up a workflow for Ploneboard Comments """
    wf.setProperties(title='Ploneboard Comment Workflow [Ploneboard]')

    for s in ('initial', 'pending', 'published', 'rejected', 'retracted'):
        wf.states.addState(s)
    for t in ('publish', 'reject', 'submit', 'autosubmit', 'autopublish', 'retract'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for script_id in script_ids:
        manage_addPythonScript(wf.scripts, script_id)
        scr = getattr(wf.scripts, script_id)
        scr.write(open(os.path.join(path_prefix, '%s.py' % script_id)).read())
    for p in (p_access, p_view, p_modify, p_addcomm, p_addpc):
        wf.addManagedPermission(p)

    wf.states.setInitialState('initial')

    #******* Set up workflow states *******
    sdef = wf.states['initial']
    sdef.setProperties(
        title='Initial state',
        transitions=('submit', 'autosubmit',))
    # Inherit from forum
    sdef.setPermission(p_access,  1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_view,    1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_modify,  1, (r_manager, r_reviewer))
    sdef.setPermission(p_addcomm, 1, (r_manager,))
    sdef.setPermission(p_addpc,   1, (r_manager,))

    sdef = wf.states['pending']
    sdef.setProperties(
        title='Waiting for reviewer',
        transitions=('publish', 'reject', 'autopublish',))
    # Nobody can reply when a comment is pending in case the comment is 'rejected'
    sdef.setPermission(p_access,  1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_view,    0, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(p_modify,  1, (r_manager, r_reviewer))
    # Acquire p_addcomm so that comment.notifyRetracted can be called. (It is protected
    # by p_addcomm.)
    sdef.setPermission(p_addcomm, 1, ())
    # But do not acquire p_addpc in order to stop anyone actually replying.
    sdef.setPermission(p_addpc,   0, ())

    sdef = wf.states['published']
    sdef.setProperties(
        title='Public',
        transitions=('retract',))
    # Inherit from forum, enables private forums
    sdef.setPermission(p_access,  1, (r_manager,))
    sdef.setPermission(p_view,    1, (r_manager,))
    sdef.setPermission(p_modify,  0, (r_manager,))
    sdef.setPermission(p_addcomm, 1, (r_manager,))
    sdef.setPermission(p_addpc,   1, (r_manager,))

    sdef = wf.states['rejected']
    sdef.setProperties(
        title='Non-visible and editable only by owner',
        transitions=('submit', 'publish',))
    sdef.setPermission(p_access,  0, (r_manager, r_owner))
    sdef.setPermission(p_view,    0, (r_manager, r_owner))
    sdef.setPermission(p_modify,  0, (r_manager, r_owner))
    sdef.setPermission(p_addcomm, 0, (r_manager,))
    sdef.setPermission(p_addpc,   0, (r_manager,))

    sdef = wf.states['retracted']
    sdef.setProperties(
        title='Retracted',
        transitions=('publish', 'submit',))
    # Inherit from forum, enables private forums
    sdef.setPermission(p_access,  1, (r_manager,))
    sdef.setPermission(p_view,    0, (r_manager, r_reviewer))
    sdef.setPermission(p_modify,  0, (r_manager,))
    sdef.setPermission(p_addcomm, 0, (r_manager,))
    sdef.setPermission(p_addpc,   0, (r_manager,))


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
        props={ 'guard_permissions':p_review })

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
        props={'guard_permissions':p_requestreview})

    tdef = wf.transitions['autosubmit']
    tdef.setProperties(
        title='Automatic publishing request',
        new_state_id='pending',
        trigger_type=TRIGGER_AUTOMATIC,
        # The submit_script is added to scripts folder by the Install script
        after_script_name='submit_script',
        actbox_name='Submit',
        actbox_url='%(content_url)s/content_submit_form',
        props={'guard_permissions':p_requestreview})

    tdef = wf.transitions['retract']
    tdef.setProperties(
        title='Retract a published comment',
        new_state_id='retracted',
        actbox_name='Retract',
        #actbox_url='%(content_url)s/content_submit_form',
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
                              p_addconv + ';' + p_review})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)


def createPloneboardCommentWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupPloneboardCommentWorkflow(ob)
    ob.setProperties(title='Comment Workflow [Ploneboard]')
    return ob

addWorkflowFactory( createPloneboardCommentWorkflow, id='ploneboard_comment_workflow'
                  , title='Comment Workflow [Ploneboard]')



def setupPloneboardConversationWorkflow(wf):
    """ Sets up a workflow for Ploneboard Conversations """
    wf.setProperties(title='Ploneboard Conversation Workflow [Ploneboard]')

    for s in ('pending', 'active', 'locked'):
        wf.states.addState(s)
    for t in ('lock', 'make_active'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for p in (p_access, p_view, p_modify, p_addcomm, p_addpc):
        wf.addManagedPermission(p)

    wf.states.setInitialState('pending')

    #******* Set up workflow states *******
    sdef = wf.states['pending']
    sdef.setProperties(
        title='Pending state',
        transitions=('make_active',))
    # This state just inherits everything from the forum workflow
    sdef.setPermission(p_access,  1, ())
    sdef.setPermission(p_view,    1, (r_manager, r_reviewer, r_owner)) # Should restrict...
    sdef.setPermission(p_modify,  0, (r_manager, r_reviewer, r_owner))
    sdef.setPermission(p_addcomm, 1, (r_manager, r_owner)) # If owner is anon everyone can?
    sdef.setPermission(p_addpc,   1, ())

    sdef = wf.states['active']
    sdef.setProperties(
        title='Active state',
        transitions=('lock',))
    # This state just inherits everything from the forum workflow
    sdef.setPermission(p_access,  1, ())
    sdef.setPermission(p_view,    1, ())
    sdef.setPermission(p_modify,  1, ())
    sdef.setPermission(p_addcomm, 1, ())
    sdef.setPermission(p_addpc,   1, ())

    sdef = wf.states['locked']
    sdef.setProperties(
        title='Locked',
        transitions=('make_active',))
    # Acquire view permissions, as we want the forum state to apply here.
    # Only let the 'special people' make any changes
    sdef.setPermission(p_access,  1, ())
    sdef.setPermission(p_view,    1, ())
    sdef.setPermission(p_modify,  0, (r_manager,))
    sdef.setPermission(p_addcomm, 0, ())

    # ***** Set up transitions *****
    tdef = wf.transitions['lock']
    tdef.setProperties(
        title='Reviewer locks conversation',
        new_state_id='locked',
        actbox_name='Lock',
        #actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_manageconv})

    tdef = wf.transitions['make_active']
    tdef.setProperties(
        title='Reviewer returns conversation to active',
        new_state_id='active',
        actbox_name='Make Active',
        #actbox_url='%(content_url)s/content_reject_form',
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
                              p_addconv + ';' + p_review})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)


def createPloneboardConversationWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupPloneboardConversationWorkflow(ob)
    ob.setProperties(title='Conversation Workflow [Ploneboard]')
    return ob

addWorkflowFactory( createPloneboardConversationWorkflow, id='ploneboard_conversation_workflow'
                  , title='Conversation Workflow [Ploneboard]')



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
    for p in (p_access, p_view, p_addconv, p_addcomm, p_addpc, p_review):
        wf.addManagedPermission(p)

    wf.states.setInitialState('memberposting')

    #******* Set up workflow states *******
    sdef = wf.states['freeforall']
    sdef.setProperties(
        title='Free for all',
        transitions=('make_memberposting', 'make_moderated', 'make_private'))
    sdef.setPermission(p_access,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_view,    1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_addconv, 1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_addcomm, 1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_addpc,   1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_review,  1, (r_manager, r_anon, r_member))

    sdef = wf.states['memberposting']
    sdef.setProperties(
        title='Require membership to post',
        transitions=('make_freeforall', 'make_moderated', 'make_private'))
    sdef.setPermission(p_access,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_view,    1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_addconv, 0, (r_manager, r_member))
    sdef.setPermission(p_addcomm, 0, (r_manager, r_member))
    sdef.setPermission(p_addpc,   1, (r_manager, r_member))
    sdef.setPermission(p_review,  0, (r_manager, r_member))

    sdef = wf.states['moderated']
    sdef.setProperties(
        title='Moderated forum',
        transitions=('make_freeforall', 'make_memberposting', 'make_private'))
    sdef.setPermission(p_access,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_view,    1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_addconv, 1, (r_manager, r_anon, r_member))
    sdef.setPermission(p_addcomm, 1, (r_manager, r_anon, r_member))
    # Give anon p_addpc, but know that they can only add comments here, and they will be moderated anyway
    sdef.setPermission(p_addpc,   1, (r_manager, r_member, r_anon))
    sdef.setPermission(p_review,  0, (r_manager, r_reviewer))

    sdef = wf.states['private']
    sdef.setProperties(
        title='Private to members only',
        transitions=('make_freeforall', 'make_memberposting', 'make_moderated'))
    sdef.setPermission(p_access,  0, (r_manager, r_member))
    sdef.setPermission(p_view,    0, (r_manager, r_member))
    sdef.setPermission(p_addconv, 0, (r_manager, r_member))
    sdef.setPermission(p_addcomm, 0, (r_manager, r_member))
    sdef.setPermission(p_addpc,   0, (r_manager, r_member))
    sdef.setPermission(p_review,  0, (r_manager, r_member))

    # ***** Set up transitions *****
    tdef = wf.transitions['make_freeforall']
    tdef.setProperties(
        title='Make the forum free for all',
        new_state_id='freeforall',
        # The publish_script is added to scripts folder by the Install script
        actbox_name='Make free-for-all',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_manage})

    tdef = wf.transitions['make_memberposting']
    tdef.setProperties(
        title='Only let members post',
        new_state_id='memberposting',
        # The make_unmoderated_script is added to scripts folder by the Install script
        actbox_name='Make member-posting',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_manage})

    tdef = wf.transitions['make_moderated']
    tdef.setProperties(
        title='Make moderated',
        new_state_id='moderated',
        # The make_moderated_script is added to scripts folder by the Install script
        actbox_name='Make moderated',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':p_manage})

    tdef = wf.transitions['make_private']
    tdef.setProperties(
        title='Private closed board',
        new_state_id='private',
        # The make_unmoderated_script is added to scripts folder by the Install script
        actbox_name='Make private',
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
                              p_addconv + ';' + p_review})

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

    # As long as ViewBoard == 'View' we don't add it
    for p in (SearchBoard, ManageBoard, ManageForum, 
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

