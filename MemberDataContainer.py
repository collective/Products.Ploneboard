try:
    from Products.CMFCore.interfaces.portal_memberdata import portal_memberdata as IMemberDataTool
    memberdatatool_interface = 1
except:
    memberdatatool_interface = 0

from Globals import InitializeClass, DTMLFile
from AccessControl import getSecurityManager, ClassSecurityInfo, Unauthorized
from Acquisition import aq_base, aq_parent, ImplicitAcquisitionWrapper
from BTrees.OOBTree import OOBTree
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from OFS.ObjectManager import ObjectManager
from ZODB.POSException import ConflictError

from Products.Archetypes.debug import log

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFMember import PKG_NAME
from Products.CMFMember.Extensions.Workflow import triggerAutomaticTransitions
from Products.CMFMember.Member import Member
from Products.CMFMember.utils import logException, changeOwnership
from DateTime import DateTime
import string

# Change this to 1 to allow TTW VariableSchemaSupport.  It is deactivated
# by default (and requires this edit for activation) b/c activation means
# that users w/ the ManageProperties privelege can execute arbitrary code
# on the server.  Do NOT activate this unless you trust your managers with
# this privelege.
expose_var_schema = 0

_marker = []

schema = BaseFolderSchema + Schema((
         TextField('description',
              default_content_type = 'text/plain',
              default_output_type = 'text/html',
              widget = TextAreaWidget(rows = 5)),

         StringField('version',
                     widget = ComputedWidget(description = "Version of this instance.",
                                             label = "Version")),
         StringField('typeName',
                     default = 'Member',
                     vocabulary = '_vocabAllowedMemberTypes',
                     read_permission = CMFCorePermissions.View,
                     accessor = 'getTypeName',
                     mutator = 'setDefaultType',
                     widget = SelectionWidget(description = "Choose default member type.",
                                              label = "Default member type")),
         LinesField('allowedMemberTypes',
                    default = ('Member',),
                    mode='rw',
                    searchable = 0,
                    vocabulary = 'all_type_names',
                    enforceVocabulary=1,
                    widget = MultiSelectionWidget(label = 'Allowed member types',
                                                  description = 'Indicate the allowed member types')),
         StringField('orphanedContentDestination',
                    vocabulary=DisplayList([('transfer_to_current', 'Transfer ownership to the person who deletes the member.'), ('delete', 'Delete the content.')]),
                    required=1,
                    default='transfer_to_current',
                    searchable=0,
                    enforceVocabulary=1,
                    widget=SelectionWidget(format='flex',
                                           label='Orphaned content',
                                           description='Indicate what should happen to a member\'s content when the member is deleted.',)
                    ),
         ))

search_catalog = 'member_catalog'
tool_types = (
    'ControlTool',
    'MemberDataContainer'
    )

class TempFolder(PortalFolder):
    portal_type = meta_type = 'MemberArea'

class MemberDataContainer(BaseBTreeFolder):

    __implements__ = (IMemberDataTool)

    schema = schema
    filter_content_types = 1
    allowed_content_types = ['Member']

    security=ClassSecurityInfo()

    id = 'portal_memberdata'
    archetype_name = meta_type = PKG_NAME + ' Container'
    portal_type = 'MemberDataContainer'

    global_allow = 0

    _defaultMember = None
    defaultMemberSchema = Member.schema
    _instanceVersion = ''

    actions = (
        { 'id': 'view',
          'name': 'View',
          'action': 'string:folder_contents',
          'permissions': (CMFCorePermissions.View,),
          'category':'object',
        },
        { 'id'            : 'orphans',
          'name'          : 'Manage orphans',
          'action'        : 'string:manage_orphans',
          'permissions'   : (CMFCorePermissions.ManageProperties,),
          'category'      : 'object',
        },)

    manage_options=( BaseBTreeFolder.manage_options +
                     ActionProviderBase.manage_options
                     )
    

    if expose_var_schema:
        manage_options += ({'label':'Schema','action':'schemaForm'}, )
        security.declareProtected(CMFCorePermissions.ManageProperties, 'schemaForm')
        schemaForm = DTMLFile('dtml/schemaForm',globals())

    # Methods: wrapUser, getMemberDataContents and pruneMemberDataContents
    # Implementation of CMFCore.interfaces.portal_memberdata.portal_memberdata
    security.declarePrivate('wrapUser')
    def wrapUser(self, user):
        """
        If possible, returns the Member object that corresponds
        to the given User object.
        """
        try:
            name = user.getUserName()
            m = self.get(name, None)
            if not m:
                ## XXX Delegate to the factory and create a new site specific
                ## member object for this user
                addMember=getMemberFactory(self, self.getTypeName())
                addMember(name)
                m = self.get(name)
                m.setUser(user)
                # trigger any workflow transitions that need to occur
                triggerAutomaticTransitions(m)

            # Return a wrapper with self as containment and
            # the user as context following CMFCore portal_memberdata
            return m.__of__(self).__of__(user)
        except:
            import traceback
            import sys
            sys.stdout.write('\n'.join(traceback.format_exception(*sys.exc_info())))
            raise

    security.declareProtected(CMFCorePermissions.ManageProperties,
                              'getMemberDataContents')
    def getMemberDataContents(self):
        """
        Returns a list containing a dictionary with information
        about the _members BTree contents: member_count is the
        total number of member instances stored in the memberdata-
        tool while orphan_count is the number of member instances
        that for one reason or another are no longer in the
        underlying acl_users user folder.
        The result is designed to be iterated over in a dtml-in
        """

        members = self.objectValues()
        oc = 0
        member_ids = []
        for member in members:
            if member.isOrphan(): oc +=1
            member_ids.append(member.getUserName())

        return [{
            'member_count' : len(member_ids),
            'orphan_count' : oc
            }]

    security.declareProtected(CMFCorePermissions.ManageProperties,
                              'pruneMemberDataContents')
    def pruneMemberDataContents(self):
        """
        Check for every Member object if it's orphan and delete it.

        The impl can override the pruneOrphan(id) method to do things
        like manage its workflow state. The default impl will remove.
        """

        members = self.objectValues()
        for member in members:
            if member.isOrphan():
                self.pruneOrphan(member.getUserName())

    def fixOwnership(self):
        """
        A utility method for transferring ownership for users who no longer
        exist
        """

        portal = getToolByName(self, 'portal_url').getPortalObject()
        catalog = getToolByName(self, 'portal_catalog')

        missing_users = []

        users = catalog.uniqueValuesFor('indexedOwner')
        for u in users:
            sp = u.split('/')
            user_id = sp[-1]
            path = '/'.join(sp[:-1])
            acl_users = portal.unrestrictedTraverse(path)
            user = acl_users.getUser(user_id)
            if user is None:
                missing_users.append(user_id)

        reindex = []
        for u in missing_users:
            ownedObjects = catalog.search({'indexedOwner':u})

            for o in ownedObjects:
                object = o.getObject()
                if object is not None and object != self:
                    if self.handleOrphanedContent(object):
                        reindex.append(object)

        for o in reindex:
            o.reindexObject()


    def handleOrphanedContent(self, object, new_user=None):
        """
        Handle orphaned content.  If new_user is not None, ownership is
        transferred to the new user.  If new_user is None, the policy is
        determined by container properties.  Returns 1 if the object's
        ownership changes.
        """
        if new_user:
            changeOwnership(object, new_user)
            return 1
        else:
            if self.getOrphanedContentDestination() == 'delete':
                try:
                    parent = aq_parent(aq_inner(object))
                    if parent.isPrincipiaFolderish:
                        parent.manage_delObjects([object.getId()])
                except ConflictError:
                    raise
                except:
                    logException()
                return 0
            else:
                member = getToolByName(self,
                                       'portal_membership').getAuthenticatedMember()
                new_user = member.getUser()
                changeOwnership(object, new_user)
                return 1

    security.declarePublic('index_html')
    def index_html(self, REQUEST, RESPONSE):
        """
        Return Member search form as default page.
        """
        search_form = self.restrictedTraverse('member_search_form')
        return search_form(REQUEST, RESPONSE)


    security.declarePrivate('_deleteMember')
    def _deleteMember(self, id):
        """
        Remove a member
        """
        self._delObject(id)

    # XXX This is untested implementation.
    ### and what uses this? should I test it?
    security.declarePrivate( 'searchMemberDataContents' )
    def searchMemberDataContents( self, search_param, search_term ):
        """
        Search members
        """

        results=[]
        if search_param == 'username':
            search_param = 'getId'

        catalog=getToolByName(self, search_catalog)
        indexes=catalog.indexes()
        query={}

        if search_param in indexes:
            query[search_param] = search_term

        if query:
            query['portal_type'] = allowed_content_types
            results=catalog(query)

        return [{'username':getattr(r,'id'),'email':getattr(r,'email')} \
                for r in [r.getObject() for r in results] if hasattr(r,'id')]


    def searchForMembers( self, REQUEST=None, **kw ):
        """
        Do a catalog search on a sites members. If the keyword brains is set
        to a non zero/null value, search will return only member_catalog metadata.
        Otherwise, memberdata objects returned.
        """

        if REQUEST:
            search_dict = getattr(REQUEST, 'form', REQUEST)
        else:
            REQUEST = {}
            search_dict = kw

        results=[]
        catalog=getToolByName(self, search_catalog)

        # no reason to iterate over all those indexes
        try:
            from sets import Set
            indexes=Set(catalog.indexes())
            indexes = indexes & Set(search_dict.keys())
        except:
            # Unless we are on 2.3
            catalog.indexes()

        query={}

        def dateindex_query(field_value, field_usage):
            usage, val = field_usage.split(':')
            return { 'query':  field_value, usage:val }

        def zctextindex_query(field_value):
            # Auto Globbing
            if not field_value.endswith('*') and field_value.find(' ') == -1:
                field_value += '*'
            return field_value

        special_query = dict((
            ( 'DateIndex',    dateindex_query ),
            ( 'ZCTextIndex',  zctextindex_query )
            ))

        if search_dict:
            # Make a indexname: fxToApply dict
            idx_fx = dict(\
                [(x.id, special_query[x.meta_type])\
                 for x in catalog.Indexes.objectValues()\
                 if (x.meta_type in special_query.keys() and x.id in indexes)]\
                )

            for i in indexes:
                val=search_dict.get(i, None)
                usage_val = search_dict.get('%s_usage' %i)
                if type(val) == type([]):
                    val = filter(None, val)

                if (i in idx_fx.keys() and val):
                    if usage_val:
                        val = idx_fx[i](val, usage_val)
                    else:
                        val = idx_fx[i](val)

                if val:
                    query.update({i:val})

        results=catalog(query) 

        if results and not (search_dict.has_key('brains') \
                            or REQUEST.get('brains', None)):
            results = [r.getObject() for r in results]

        return filter(None, results)

    security.declarePrivate('registerMemberData')
    def registerMemberData(self, m, id):
        """
        Adds the given member data to the _members dict.
        This is done as late as possible to avoid side effect
        transactions and to reduce the necessary number of
        entries.
        """
        self._setObject(id, m)

    def _getMemberInstance(self):
        """Get an instance of the Member class.  Used for
           extracting default property values, etc."""
        if self._defaultMember is None:
            tempFolder = PortalFolder('temp').__of__(self)
            getMemberFactory(tempFolder, self.getTypeName())('cmfmemberdefault')
            self._defaultMember = getattr(tempFolder,'cmfmemberdefault')
            getattr(tempFolder,'cmfmemberdefault').unindexObject()
            # don't store _defaultMember in the catalog
            tempFolder.unindexObject()
            # don't store _defaultMember in the catalog
            self._defaultMember.unindexObject()
        return self._defaultMember


    ## Folderish Methods

#     security.declareProtected(CMFCorePermissions.AddPortalContent, 'invokeFactory')
#     def invokeFactory( self
#                      , type_name
#                      , id
#                      , RESPONSE=None
#                      , *args
#                      , **kw
#                      ):
#         """
#         Overriding invokeFactory to be able to have different Member types per
#         instance base. We do a change in the portal_types.MemberDataContainer's
#         allowed content types before we add a new member. After the creation we
#         change to default value.
#         """
#         portal_types = getToolByName(self, 'portal_types')
#         type_info = portal_types.getTypeInfo('MemberDataContainer')
#         old_content_types = type_info.allowed_content_types
#         type_info.allowed_content_types = self.getAllowedMemberTypes()
#         new_id = BaseBTreeFolder.invokeFactory(self, type_name, id, RESPONSE, *args, **kw)
#         type_info.allowed_content_types = old_content_types
#         return new_id

    def allowedContentTypes(self):
        """
        Returns a list of TypeInfo objects for the specified types in
        allowedMemberTypes. This method is used to get a list of addable
        objects in i.e. Plone.
        """
        result = []
        portal_types = getToolByName(self, 'portal_types')
        for contentType in self.getAllowedMemberTypes():
            result.append(portal_types.getTypeInfo(contentType))
        return result

    # Removed since we now can control allowed content types per instance
    # It could and should be use when the in & out widget is available to
    # populate vocabulary for allowed content types.
    def all_type_names(self):
        """
        Get vocabulary for allowed member types
        """

        return getToolByName(self, 'cmfmember_control').getAvailableMemberTypes()

    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        allowedTypes = [self._getMemberInstance()._getTypeName()]
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in allowedTypes:
                meta_types.append(meta_type)
        return meta_types

    
    security.declareProtected(CMFCorePermissions.ListPortalMembers, 'contentValues')
    def contentValues(self, spec=None, filter=None):
        objects = [v.__of__(self) for v in self.objectValues(spec=spec)]
        l = []
        for v in objects:
            id = v.getId()
            try:
                if getSecurityManager().validate(self, self, id, v):
                    l.append(v)
            except Unauthorized:
                pass
        return l


    def _checkId(self, id, allow_dup=0):
        PortalFolder._checkId(self, id, allow_dup)
        BaseBTreeFolder._checkId(self, id, allow_dup)


    # register type type of Member object that the MemberDataConatiner will store
    def registerType(self, new_type_name, default=1):
        if default:
            self.setDefaultType(new_type_name)
        typestool=getToolByName(self, 'portal_types')
        act = typestool.MemberDataContainer.allowed_content_types
        if new_type_name not in act:
            act = act + (new_type_name,)
        typestool.MemberDataContainer.allowed_content_types = act


    def setDefaultType(self, type_name):
        self.typeName = type_name
        t_tool = getToolByName(self, 'portal_types')
        at_tool = getToolByName(self, 'archetype_tool')
        type_info = t_tool.getTypeInfo(type_name)
        pkg = type_info.product
        self.defaultMemberSchema = at_tool.lookupType(pkg, type_name)['schema']
        self._defaultMember = None # nuke the default member (which was of the old Member type)

    # Migrate members when changing member type
    # 1) rename old member to some temp name
    # 2) create new member with old id
    # 3) transfer user assets to new member
    # 4) delete old member
    #
    # new_type_name = meta_type for the new Member type
    # workflow_transfer = dict mapping each state in old members to a list of transitions
    #       that must be executed to move the new member to the old member's state
    def migrateMembers(self, out, new_type_name, workflow_transfer={}):

        self.registerType(new_type_name)
        factory = getMemberFactory(self, self.getTypeName())

        portal = getToolByName(self, 'portal_url').getPortalObject()
        workflow_tool = getToolByName(self, 'portal_workflow')

        for m in self.objectIds():
            old_member = self.get(m)
            temp_id = 'temp_' + m
            while self.get(temp_id):
                temp_id = '_' + temp_id
            old_member._migrating = 1
            self.manage_renameObjects([m], [temp_id])
            factory(m)
            old_member = self.get(temp_id)
            new_member = self.get(m)
            # copy over old member attributes
            new_member._migrate(old_member, [], out)

            # copy workflow state
            old_member_state = workflow_tool.getInfoFor(old_member,
                                                        'review_state', '')
            print >> out, 'state = %s' % (old_member_state,)
            transitions = workflow_transfer.get(old_member_state, [])
            print >> out, 'transitions = %s' % (str(transitions),)
            for t in transitions:
                workflow_tool.doActionFor(new_member, t)

            self.manage_delObjects(temp_id)
        from Products.CMFMember.Extensions.Install import setupNavigation
        setupNavigation(self, out, new_type_name)


    #################################
    # version awareness

    def setVersion(self, version):
        self._instanceVersion = version

    def getVersion(self):
        return self._instanceVersion or 'development'


    ##SUBCLASS HOOKS
    security.declarePrivate('pruneOrphan')
    def pruneOrphan(self, id):
        """
        Called when a member object exists for something not in the
        acl_users folder
        """
        self._deleteMember(id)


    if expose_var_schema:
        security.declareProtected(CMFCorePermissions.ManageProperties,
                                  'setMemberSchema')
    else:
        security.declarePrivate('setMemberSchema')
    def setMemberSchema(self,member_schema,REQUEST=None):
        """
        Takes a string containing python code which defines a schema.  This
        string is eval'ed and the resulting schema is appended to the default
        Member schema.
        """
        member_schema=member_schema.strip().replace('\r','')
        schema=eval(member_schema)
        self.memberSchema=self.defaultMemberSchema + schema
        self.member_schema=member_schema

        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(CMFCorePermissions.View,
                              'getMemberSchema')
    def getMemberSchema(self):
        """
        Returns acquisition wrapped member schema.
        """
        schema = getattr(self,'memberSchema',self.defaultMemberSchema )
        schema = ImplicitAcquisitionWrapper(schema, self)
        return schema

    # AT methods
    def setAllowedMemberTypes(self, memberTypes, **kwargs):
        """
        Overriding default mutator since TypesTool checks the
        variable allowed_content_types directly.  No checking
        for whether types are real, proper, etc.
        """


        self.allowed_content_types = memberTypes
        field=self.Schema()['allowedMemberTypes']
        field.set(self, memberTypes, **kwargs)

        type_tool = getToolByName(self, 'portal_types')
        
        mdc = type_tool.getTypeInfo(self)
        mdc.manage_changeProperties(allowed_content_types=memberTypes)

    def _vocabAllowedMemberTypes(self):
        return self.getAllowedMemberTypes()

# Put this outside the MemberData tool so that it can be used for
# conversion of old MemberData during installation
def getMemberFactory(self, type_name):
    """
    Return a callable that is the registered object returning a
    contentish member object
    """
    # Assumptions: there is a types_tool type called Member, you
    # want one of these in the folder, changing this changes the
    # types of members in your site.
    types_tool = getToolByName(self, 'portal_types')
    ti = types_tool.getTypeInfo(type_name)

    try:
        p = self.manage_addProduct[ti.product]
        action = getattr(p, ti.factory, None)
    except AttributeError:
        raise ValueError, 'No type information installed'
    if action is None:
        raise ValueError, ('Invalid Factory for %s'
                           % ti.getId())
    return action


#from Products.CMFCore.utils import _verifyActionPermissions
#
## XXX update this for 1.1
#def _getViewFor(obj, view='view', default=None):
#    ti = obj.getTypeInfo()
#    if ti is not None:
#        actions = ti.listActions()
#        for action in actions:
#            if action.get('id', None) == default:
#                if default and type(default) != type(''):
#                    default = default['action']
#                return obj.restrictedTraverse(default)
#
#        # "view" action is not present or not allowed.
#        # Find something that's allowed.
#        #for action in actions:
#        #    if _verifyActionPermissions(obj, action)  and action.get('action','')!='':
#        #        return obj.restrictedTraverse(action['action'])
#        raise 'Unauthorized', ('No accessible views available for %s' %
#                               '/'.join(obj.getPhysicalPath()))
#    else:
#        raise 'Not Found', ('Cannot find default view for "%s"' %
#                            '/'.join(obj.getPhysicalPath()))


registerType(MemberDataContainer)
