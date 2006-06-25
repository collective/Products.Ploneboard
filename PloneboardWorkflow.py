import os
from Globals import package_home

from Products.Ploneboard.config import GLOBALS
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from permissions import ViewBoard, SearchBoard, ManageBoard, AddForum, ManageForum,\
     AddConversation, AddComment, EditComment, ManageConversation, DeleteComment, \
     ManageComment, ApproveComment, RetractComment, RequestReview, ModerateForum
from Products.CMFCore.permissions import View, AccessContentsInformation, ModifyPortalContent
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC
from Products.CMFCore.permissions import AddPortalContent
from Products.ExternalMethod.ExternalMethod import ExternalMethod


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
    for p in (AccessContentsInformation, ViewBoard, EditComment, AddComment, AddPortalContent, DeleteComment):
        wf.addManagedPermission(p)

    wf.states.setInitialState('initial')

    #******* Set up workflow states *******
    sdef = wf.states['initial']
    sdef.setProperties(
        title='Being created',
        transitions=('submit', 'autosubmit',))
    # Inherit from forum
    sdef.setPermission(AccessContentsInformation,  1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(ViewBoard,    0, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(EditComment,  1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(AddComment, 0, ())
    sdef.setPermission(AddPortalContent,   0, (r_manager,))
    sdef.setPermission(DeleteComment,   0, (r_manager, r_owner, r_reviewer))

    sdef = wf.states['pending']
    sdef.setProperties(
        title='Waiting for moderator',
        transitions=('publish', 'reject', 'autopublish',))
    # Nobody can reply when a comment is pending in case the comment is 'rejected'
    sdef.setPermission(AccessContentsInformation,  1, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(ViewBoard,    0, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(EditComment,  0, (r_manager, r_owner, r_reviewer))
    # Acquire AddComment so that comment.notifyRetracted can be called. (It is protected
    # by AddComment.)
    sdef.setPermission(AddComment, 0, ())
    # But do not acquire AddPortalContent in order to stop anyone actually replying.
    sdef.setPermission(AddPortalContent,   0, ())
    sdef.setPermission(DeleteComment,   0, (r_manager, r_owner, r_reviewer))

    sdef = wf.states['published']
    sdef.setProperties(
        title='Public',
        transitions=('retract',))
    # Inherit from forum, enables private forums
    sdef.setPermission(AccessContentsInformation,  1, (r_manager,))
    sdef.setPermission(ViewBoard,    1, (r_manager,))
    sdef.setPermission(EditComment,  0, (r_manager, r_owner))
    sdef.setPermission(AddComment, 1, ())
    sdef.setPermission(AddPortalContent,   1, (r_manager,))
    sdef.setPermission(DeleteComment,   0, (r_manager, r_owner, r_reviewer))

    sdef = wf.states['rejected']
    sdef.setProperties(
        title='Rejected',
        transitions=('submit',))
    sdef.setPermission(AccessContentsInformation,  0, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(ViewBoard,    0, (r_manager, r_owner, r_reviewer))
    sdef.setPermission(EditComment,  0, (r_manager, r_owner))
    sdef.setPermission(AddComment, 0, ())
    sdef.setPermission(AddPortalContent,   0, (r_manager,))
    sdef.setPermission(DeleteComment,   0, (r_manager, r_owner, r_reviewer))

    sdef = wf.states['retracted']
    sdef.setProperties(
        title='Retracted',
        transitions=('publish', 'submit',))
    # Inherit from forum, enables private forums
    sdef.setPermission(AccessContentsInformation,  1, (r_manager, r_reviewer, r_owner))
    sdef.setPermission(ViewBoard,    0, (r_manager, r_reviewer, r_owner))
    sdef.setPermission(EditComment,  0, (r_manager, r_reviewer, r_owner))
    sdef.setPermission(AddComment, 0, ())
    sdef.setPermission(AddPortalContent,   0, (r_manager,))
    sdef.setPermission(DeleteComment,   0, (r_manager, r_owner, r_reviewer))

    # ***** Set up transitions *****
    tdef = wf.transitions['publish']
    tdef.setProperties(
        title='Reviewer publishes content',
        new_state_id='published',
        # The publish_script is added to scripts folder by the Install script
        after_script_name='publish_script',
        actbox_name='Publish',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':ApproveComment})

    tdef = wf.transitions['autopublish']
    tdef.setProperties(
        title='Automatic publishing in unmoderated boards',
        new_state_id='published',
        trigger_type=TRIGGER_AUTOMATIC,
        # The autopublish_script is added to scripts folder by the Install script
        after_script_name='autopublish_script',
        props={ 'guard_permissions':ApproveComment })

    tdef = wf.transitions['reject']
    tdef.setProperties(
        title='Reviewer rejects submission',
        new_state_id='rejected',
        # The reject_script is added to scripts folder by the Install script
        after_script_name='reject_script',
        actbox_name='Reject',
        actbox_url='%(content_url)s/content_reject_form',
        props={'guard_permissions':ApproveComment})

    tdef = wf.transitions['submit']
    tdef.setProperties(
        title='Member requests publishing',
        new_state_id='pending',
        actbox_name='Submit',
        actbox_url='%(content_url)s/content_submit_form',
        props={'guard_permissions':RequestReview})

    tdef = wf.transitions['autosubmit']
    tdef.setProperties(
        title='Automatic publishing request',
        new_state_id='pending',
        trigger_type=TRIGGER_AUTOMATIC,
        actbox_name='Submit',
        actbox_url='%(content_url)s/content_submit_form',
        props={'guard_permissions':RequestReview})

    tdef = wf.transitions['retract']
    tdef.setProperties(
        title='Retract a published comment',
        new_state_id='retracted',
        actbox_name='Retract',
        #actbox_url='%(content_url)s/content_submit_form',
        props={'guard_permissions':RetractComment})

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
                              AddConversation + ';' + ApproveComment})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

    # Script Initialization
    wf.scripts._setObject('autopublish_script',
                          ExternalMethod('autopublish_script', 'autopublish_script',
                                         'Ploneboard.WorkflowScripts', 'autopublish_script'))
    
    wf.scripts._setObject('publish_script',
                          ExternalMethod('publish_script', 'publish_script',
                                         'Ploneboard.WorkflowScripts', 'publish_script'))
    
    wf.scripts._setObject('reject_script',
                          ExternalMethod('reject_script', 'reject_script',
                                         'Ploneboard.WorkflowScripts', 'reject_script'))


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

    for s in ('pending', 'active', 'locked', 'rejected'):
        wf.states.addState(s)
    for t in ('lock', 'publish', 'reject'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for p in (AccessContentsInformation, ViewBoard, EditComment, AddComment, AddPortalContent):
        wf.addManagedPermission(p)

    wf.states.setInitialState('pending')

    #******* Set up workflow states *******
    sdef = wf.states['pending']
    sdef.setProperties(
        title='Pending state',
        transitions=('publish', 'reject',))
    # This state just inherits everything from the forum workflow
    sdef.setPermission(AccessContentsInformation,  1, ())
    sdef.setPermission(ViewBoard,    0, (r_manager, r_reviewer, r_owner))
    sdef.setPermission(EditComment,  0, (r_manager, r_reviewer, r_owner))
    sdef.setPermission(AddComment, 1, (r_manager, r_owner)) # If owner is anon everyone can?
    sdef.setPermission(AddPortalContent,   1, ())

    sdef = wf.states['active']
    sdef.setProperties(
        title='Active',
        transitions=('lock',))
    # This state just inherits everything from the forum workflow
    sdef.setPermission(AccessContentsInformation,  1, ())
    sdef.setPermission(ViewBoard,    1, ())
    sdef.setPermission(EditComment,  1, ())
    sdef.setPermission(AddComment, 1, ())
    sdef.setPermission(AddPortalContent,   1, ())

    sdef = wf.states['locked']
    sdef.setProperties(
        title='Locked',
        transitions=('publish',))
    # Acquire view permissions, as we want the forum state to apply here.
    # Only let the 'special people' make any changes
    sdef.setPermission(AccessContentsInformation,  1, ())
    sdef.setPermission(ViewBoard,    1, ())
    sdef.setPermission(EditComment,  0, (r_manager,))
    sdef.setPermission(AddComment, 0, ())
    sdef.setPermission(AddPortalContent, 0, ())

    sdef = wf.states['rejected']
    sdef.setProperties(
        title='Rejected',
        transitions=('publish',))
    # This state just inherits everything from the forum workflow
    sdef.setPermission(AccessContentsInformation,  1, ())
    sdef.setPermission(ViewBoard,    0, (r_manager, r_reviewer, r_owner))
    sdef.setPermission(EditComment,  0, (r_manager, r_owner))
    sdef.setPermission(AddComment, 0, ())
    sdef.setPermission(AddPortalContent,   0, ())

    # ***** Set up transitions *****
    tdef = wf.transitions['lock']
    tdef.setProperties(
        title='Reviewer locks conversation',
        new_state_id='locked',
        actbox_name='Lock',
        #actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':ManageConversation})

    tdef = wf.transitions['publish']
    tdef.setProperties(
        title='Reviewer returns conversation to active',
        new_state_id='active',
        actbox_name='Activate',
        #actbox_url='%(content_url)s/content_reject_form',
        props={'guard_permissions':ApproveComment})

    tdef = wf.transitions['reject']
    tdef.setProperties(
        title='Reviewer rejects pending conversation',
        new_state_id='rejected',
        actbox_name='Reject',
        #actbox_url='%(content_url)s/content_reject_form',
        props={'guard_permissions':ApproveComment})

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
                              AddConversation + ';' + ApproveComment})

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
    for p in (AccessContentsInformation, ViewBoard, AddConversation, 
                AddComment, AddPortalContent, ApproveComment, RetractComment, ModerateForum,):
        wf.addManagedPermission(p)

    wf.states.setInitialState('memberposting')

    #******* Set up workflow states *******
    sdef = wf.states['freeforall']
    sdef.setProperties(
        title='Free for all',
        transitions=('make_memberposting', 'make_moderated', 'make_private'))
    sdef.setPermission(AccessContentsInformation,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(ViewBoard,    1, (r_manager, r_anon, r_member))
    sdef.setPermission(AddConversation, 1, (r_manager, r_anon, r_member))
    sdef.setPermission(AddComment, 1, (r_manager, r_anon, r_member))
    sdef.setPermission(AddPortalContent,   1, (r_manager, r_anon, r_member))
    sdef.setPermission(ApproveComment,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(RetractComment,  0, ())
    sdef.setPermission(ModerateForum,  0, ())

    sdef = wf.states['memberposting']
    sdef.setProperties(
        title='Require membership to post',
        transitions=('make_freeforall', 'make_moderated', 'make_private'))
    sdef.setPermission(AccessContentsInformation,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(ViewBoard,    1, (r_manager, r_anon, r_member))
    sdef.setPermission(AddConversation, 0, (r_manager, r_member))
    sdef.setPermission(AddComment, 0, (r_manager, r_member))
    sdef.setPermission(AddPortalContent,   1, (r_manager, r_member))
    sdef.setPermission(ApproveComment,  0, (r_manager, r_member))
    sdef.setPermission(RetractComment,  0, ())
    sdef.setPermission(ModerateForum,  0, ())

    sdef = wf.states['moderated']
    sdef.setProperties(
        title='Moderated forum',
        transitions=('make_freeforall', 'make_memberposting', 'make_private'))
    sdef.setPermission(AccessContentsInformation,  1, (r_manager, r_anon, r_member))
    sdef.setPermission(ViewBoard,    1, (r_manager, r_anon, r_member))
    sdef.setPermission(AddConversation, 1, (r_manager, r_anon, r_member))
    sdef.setPermission(AddComment, 1, (r_manager, r_anon, r_member))
    # Give anon AddPortalContent, but know that they can only add comments here, and they will be moderated anyway
    sdef.setPermission(AddPortalContent,   1, (r_manager, r_member, r_anon))
    sdef.setPermission(ApproveComment,  0, (r_manager, r_reviewer))
    sdef.setPermission(RetractComment,  0, (r_manager, r_reviewer))
    sdef.setPermission(ModerateForum,  0, (r_manager, r_reviewer))

    sdef = wf.states['private']
    sdef.setProperties(
        title='Private to members only',
        transitions=('make_freeforall', 'make_memberposting', 'make_moderated'))
    sdef.setPermission(AccessContentsInformation,  0, (r_manager, r_member))
    sdef.setPermission(ViewBoard,    0, (r_manager, r_member))
    sdef.setPermission(AddConversation, 0, (r_manager, r_member))
    sdef.setPermission(AddComment, 0, (r_manager, r_member))
    sdef.setPermission(AddPortalContent,   0, (r_manager, r_member))
    sdef.setPermission(ApproveComment,  0, ())
    sdef.setPermission(ModerateForum,  0, ())

    # ***** Set up transitions *****
    tdef = wf.transitions['make_freeforall']
    tdef.setProperties(
        title='Make the forum free for all',
        new_state_id='freeforall',
        actbox_name='Make free-for-all',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':ManageForum})

    tdef = wf.transitions['make_memberposting']
    tdef.setProperties(
        title='Only let members post',
        new_state_id='memberposting',
        actbox_name='Make member-posting',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':ManageForum})

    tdef = wf.transitions['make_moderated']
    tdef.setProperties(
        title='Make moderated',
        new_state_id='moderated',
        actbox_name='Make moderated',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':ManageForum})

    tdef = wf.transitions['make_private']
    tdef.setProperties(
        title='Private closed board',
        new_state_id='private',
        actbox_name='Make private',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':ManageForum})

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
                              AddConversation + ';' + ApproveComment})

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
    wf.setProperties(title='Ploneboard Workflow [Ploneboard]')

    for s in ('private', 'published',):
        wf.states.addState(s)
    for t in ('open', 'hide',):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    
    # As long as ViewBoard == 'View' we don't add it
    for p in (AccessContentsInformation, ModifyPortalContent, AddPortalContent,
              ViewBoard, SearchBoard, ManageBoard, ManageForum, 
              AddConversation, AddComment, EditComment, 
              ManageConversation, ManageComment, ApproveComment):
        wf.addManagedPermission(p)

    wf.states.setInitialState('published')

    sdef = wf.states['private']
    sdef.setProperties(
        title='Hidden',
        transitions=('open',))
    sdef.setPermission(AccessContentsInformation,  0, (r_manager, r_owner))
    sdef.setPermission(ModifyPortalContent,        0, (r_manager, r_owner))
    sdef.setPermission(AddPortalContent,           0, (r_manager, r_owner))
    sdef.setPermission(ViewBoard,                  0, (r_manager, r_owner))
    sdef.setPermission(ViewBoard,                  0, (r_manager, r_owner))
    sdef.setPermission(SearchBoard,                0, (r_manager, r_owner))
    sdef.setPermission(ManageBoard,                0, (r_manager, r_owner))
    sdef.setPermission(ManageForum,                0, (r_manager, r_owner))
    
    sdef.setPermission(AddConversation,            0, (r_manager, r_owner))
    sdef.setPermission(AddComment,                 0, (r_manager, r_owner))
    sdef.setPermission(EditComment,                0, (r_manager, r_owner))
    
    sdef.setPermission(ManageConversation,         0, (r_manager,))
    sdef.setPermission(ManageComment,              0, (r_manager, r_owner))
    sdef.setPermission(ApproveComment,             0, (r_manager, r_reviewer))

    sdef = wf.states['published']
    sdef.setProperties(
        title='Open',
        transitions=('hide',))
    sdef.setPermission(ModifyPortalContent,        0, (r_manager, r_owner))
    sdef.setPermission(AddPortalContent,           0, (r_manager, r_owner))
    sdef.setPermission(AccessContentsInformation,  1, (r_anon, r_manager))
    sdef.setPermission(ViewBoard,                  1, (r_anon, r_manager))
    sdef.setPermission(SearchBoard,                1, (r_anon, r_manager))
    sdef.setPermission(ManageBoard,                0, (r_manager, r_owner))
    sdef.setPermission(ManageForum,                0, (r_manager, r_owner))
    
    sdef.setPermission(AddConversation,            0, (r_manager, r_owner))
    sdef.setPermission(AddComment,                 0, (r_manager, r_owner))
    sdef.setPermission(EditComment,                0, (r_manager, r_owner))
    
    sdef.setPermission(ManageConversation,         0, (r_manager,))
    sdef.setPermission(ManageComment,              0, (r_manager, r_owner))
    sdef.setPermission(ApproveComment,             0, (r_manager, r_reviewer))

    # ***** Set up transitions *****
    tdef = wf.transitions['open']
    tdef.setProperties(
        title='Open message board',
        new_state_id='published',
        actbox_name='Open',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':ManageForum})

    tdef = wf.transitions['hide']
    tdef.setProperties(
        title='Hide message board',
        new_state_id='private',
        actbox_name='Hide',
        actbox_url='%(content_url)s/content_publish_form',
        props={'guard_permissions':ManageForum})
    
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
                              AddConversation + ';' + ApproveComment})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

def createPloneboardWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupPloneboardWorkflow(ob)
    ob.setProperties(title='Ploneboard Workflow [Ploneboard]')
    return ob

addWorkflowFactory( createPloneboardWorkflow, id='ploneboard_workflow'
                  , title='Ploneboard Workflow [Ploneboard]')

