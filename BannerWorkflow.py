from Products.CMFCore.CMFCorePermissions import \
        AccessContentsInformation, ModifyPortalContent, View

from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

from BannerPermissions import *

BANNER_WORKFLOW_ID = 'banner_workflow'
BANNER_WORKFLOW_TITLE = 'Banner Workflow [PloneBannerManager]'

ADMIN_ROLES = ('Owner', 'Manager', bannerManager)
ALL_ROLES = ('Anonymous', 'Member', 'Owner', 'Manager', bannerManager)

def setupBannerWorkflow(wf):
    wf.setProperties(title=BANNER_WORKFLOW_TITLE)

    for s in ('private', 'published'):
        wf.states.addState(s)
    for t in ('publish', 'hide'):
        wf.transitions.addTransition(t)
    for v in ('action', 'actor', 'comments', 'review_history', 'time'):
        wf.variables.addVariable(v)
    for p in (AccessContentsInformation, ModifyPortalContent, View):
        wf.addManagedPermission(p)

    wf.states.setInitialState('private')

    # state definitions
    sdef = wf.states['private']
    sdef.setProperties(
            title='Visible and editable only by owner or manager',
            transitions=('publish',))
    sdef.setPermission(AccessContentsInformation, 0, ADMIN_ROLES)
    sdef.setPermission(ModifyPortalContent, 0, ADMIN_ROLES)
    sdef.setPermission(View, 0, ADMIN_ROLES)

    sdef = wf.states['published']
    sdef.setProperties(
            title='Public',
            transitions=('hide',))
    sdef.setPermission(AccessContentsInformation, 0, ALL_ROLES)
    sdef.setPermission(ModifyPortalContent, 0, ADMIN_ROLES)
    sdef.setPermission(View, 0, ALL_ROLES)

    # transition definitions
    tdef = wf.transitions['publish']
    tdef.setProperties(
            title='Make content public',
            new_state_id='published',
            actbox_name='Publish',
            props={'guard_permissions':ManageBanners})

    tdef = wf.transitions['hide']
    tdef.setProperties(
            title='Hide content',
            new_state_id='private',
            actbox_name='Hide',
            props={'guard_permissions':ManageBanners})

    # variable definitions
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
                       props={'guard_permissions': ManageBanners})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

def createBannerWorkflow(id):
    wf = DCWorkflowDefinition(id)
    setupBannerWorkflow(wf)
    return wf

addWorkflowFactory(createBannerWorkflow, id=BANNER_WORKFLOW_ID,
                   title=BANNER_WORKFLOW_TITLE)
