from AccessControl import ClassSecurityInfo
from Products.CMFTypes import registerType
from Products.CMFTypes.BaseContent import BaseContent
from Products.CMFTypes.ExtensibleMetadata import ExtensibleMetadata
from Products.CMFTypes.Field       import *
from Products.CMFTypes.Form        import *
from Products.CMFTypes.debug import log
from Products.CMFTypes.Storage import IStorage
from DateTime import DateTime

def addMember(self, id, **kwargs):
    o = Member(id, **kwargs)
    # XXX
    #self._setObject(id, o)
    return o

content_type = FieldList((
    LinesField('roles',
               mutator="setRoles",
               accessor="getRoles",
               vocabulary='valid_roles',
               read_permission=CMFCorePermissions.ManagePortal,
               write_permission=CMFCorePermissions.ManagePortal,
               form_info=MultiSelectionInfo()), 
    
    LinesField('domains',
               accessor="getDomains",
               read_permission=CMFCorePermissions.ManagePortal,
               write_permission=CMFCorePermissions.ManagePortal,
               form_info=LinesInfo()),

    ObjectField('email',
                searchable=1,
                mode="rw"),
    
    ObjectField('portal_skin',
                required=1,
                searchable=0,
                vocabulary='available_skins',
                enforceVocabulary=1,
                form_info=SingleSelectionInfo(format="pulldown",
                                              label="Portal Skin")),
    
    ObjectField('listed',
                searchable=0,
                form_info=BooleanInfo(label="Listed")),

    DateTimeField('login_time',
                  accessor="getLoginTime",
                  mutator="setLoginTime",
                  searchable=0,
                  form_info=DateTimeInfo(label="Login Time",
                                         visible=-1,)),
    
    DateTimeField('last_login_time',
                  accessor="getLastLoginTime",
                  mutator="setLastLoginTime",
                  searchable=0,
                  form_info=DateTimeInfo(label="Last Login Time",
                                         visible=-1,)),

    ObjectField('wysiwyg_editor',
                vocabulary='editors',
                enforceVocabulary=1,
                form_info=SingleSelectionInfo(format="pulldown",
                                              label="WYSIWYG Editor")),
    
    ObjectField('visible_ids',
                form_info=BooleanInfo(label="Show Names")
                )
    
    ))

_marker = []

class Member(BaseContent):
    """A description of a member"""
    portal_type = meta_type = "Member"

    type = BaseContent.type + content_type + ExtensibleMetadata.type

    ##IMPL DETAILS
    def __init__(self, userid):
        BaseContent.__init__(self, userid)
        self.id = str(userid)

        now = DateTime()
        self.setLoginTime(now)
        self.setLastLoginTime(now)

    def getUser(self):
        if not hasattr(self, '_v_user'):
            self._v_user = self.acl_users.getUser(self.id).__of__(self.acl_users)
            
        return self._v_user
    
    def setUser(self, user):
        self._v_user = user

    ##USER INTERFACE IMPL
    def getUserName(self):
        """Return the username of a user"""
        return self.getUser().getUserName()

    def _getPassword(self):
        """Return the password of the user."""
        return self.getUser()._getPassword()

    def getRoles(self):
        """Return the list of roles assigned to a user."""
        return self.getUser().getRoles() + getattr(self, '_roles', ())

    def getDomains(self):
        """Return the list of domain restrictions for a user"""
        return self.getUser().getDomains()

    
    def setRoles(self, value):
        if isinstance(roles, types.StringType):
            value = roles.split('\n')
            value = [v.strip() for v in value if v.strip()]
            value = filter(None, value)

        self._roles = value

    def setDomains(self, value):
        self.getUser().setDomains(value)
    
    ## Contract with portal_membership
    
    def setProperties(self, mapping=None, **kwargs):
        """assign all the props to member attributes, we expect
        to be able to find a mutator for each of these props
        """
        #We know this is a CMFTypes based object so we look for
        #mutators there first
        if kwargs:
            # mapping could be a request object thats not really a dict,
            # this is what we get
            data = {}
            for k,v in mapping.form.items():
                data[k] = v
            data.update(kwargs)
            mapping = data
            

        for key, value in mapping.items():
            field = self.type.get(key)
            mutator = None
            if field:
                mutator = getattr(self, field.mutator, None)
                if not mutator:
                    # Oops? Try the pattern 'setFoo'
                    mutator = getattr(self, 'set%s' % key.capitalize(), None)

            if mutator:
                mutator(value)
            else:
                # XXX fall back to properties? or attributes
                pass

    def setMemberProperties(self, mapping):
        self.setProperties(mapping)

    def getProperty(self, id, default=_marker):
        #assume CMFTypes attr here 
        accessor = getattr(self, self.type[id].accessor, None)
        try:
            value = accessor()
        except:
            if default is _marker:
                raise AttributeError(id)
            value = default

        return value
    
        
    def getMemberId(self):
        return self.getUserName()

    #Vocab methods
    def editors(self):
        return self.portal_properties.site_properties.available_editors
    
    def valid_roles(self):
        return self.getUser().valid_roles()

    def available_skins(self):
        return self.portal_skins.getSkinSelections()

    ##
    def __str__(self):
        return self.id
    
    def __call__(self, *args, **kwargs):
        return ''
    
registerType(Member)

