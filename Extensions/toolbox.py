from Products.CMFCore.utils import getToolByName
from Products.CMFMember.config import *
from Products.CMFMember.MemberDataContainer import MemberDataContainer

from Globals import InitializeClass

class SetupMember:

    """
    utility class for configuring members

    call methods separately or in one fell swoop


    0. Setup default member:

       SetupMember()()


    0. Setup a member type: 

        SetupMember(member_type='Freemason', workflow='Initiation')()


    0. reconfigure a member type:

        reMason = MemberSetup(member_type='FreeMason')
        reMason.setWorkflow('Long Initiation')

    0. setup a member, but don't register as the portal default

        print reMason(is_default=False)
        
        'set type: Freemason, workflow->Long Iniation, catalogs->['member_catalog', 'portal_catalog'] '
    """

    def __init__(self, context, member_type=DEFAULT_TYPE, **kw):
        """ context is normally a portal object """
        self.type = member_type
        self.workflow = DEFAULT_WORKFLOW
        self.catalogs = DEFAULT_CATALOGS
        self.is_default = True
        self.register = True
        self.context = context
        if kw:
            self.set(**kw)

    def finish(self):
        self.setCatalogs()
        self.setupPortalFactoryProps()
        
        if self.register:
            cmfmember_tool = getToolByName(self.context, 'cmfmember_control')  
            cmfmember_tool.upgrade( swallow_errors=0,
                                    default_member_type=self.type,
                                    default_workflow=self.workflow)
        else:
            # for situations where instant migration is not desired
            # ie. when CMFMember is installed for the first time
            
            self.setWorkflow()
            mdc = getToolByName(self.context, 'portal_memberdata')
            if mdc.meta_type == MemberDataContainer.meta_type:
                mdc.setDefaultType(self.type)
                
        return "set %s: workflow->%s, catalogs->%s" %(self.type,
                                                     self.workflow,
                                                     self.catalogs) 

    def set(self, **kw):
        [setattr(self, key, val) for key, val in kw.items()]

    def __call__(self, **kw):
        """ set all, do all """
        if kw:
            self.set(**kw)
        
        return self.finish()

    def setWorkflow(self, workflow=None):
        if workflow:
            self.workflow = workflow
            
        wf_tool = getToolByName(self.context, 'portal_workflow')
        wf_tool.setChainForPortalTypes((self.type,), self.workflow)
        wf_tool.updateRoleMappings()

    def setCatalogs(self, catalogs=None):
        if catalogs:
            self.catalogs = catalogs
            
        at = getToolByName(self.context, 'archetype_tool')
        at.setCatalogsByType(self.type, self.catalogs)

    def setupPortalFactoryProps(self):
        site_props = getToolByName(self.context, 'portal_properties').site_properties
        if not hasattr(site_props,'portal_factory_types'):
            site_props._setProperty('portal_factory_types',('MemberTest',), 'lines')
        else:
            factory_types = list(site_props.getProperty('portal_factory_types'))
            if self.type not in factory_types:
                factory_types.append(self.type)
                factory_types = tuple(factory_types)
                site_props.manage_changeProperties(portal_factory_types=factory_types)



InitializeClass(SetupMember)
