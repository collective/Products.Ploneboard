import random
import re
import md5
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.RegistrationTool import RegistrationTool as BaseTool

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager, PermissionRole, Unauthorized
from Products.CMFCore import CMFCorePermissions
from MemberPermissions import MAIL_PASSWORD_PERMISSION, ADD_MEMBER_PERMISSION
# - remove '1', 'l', and 'I' to avoid confusion
# - remove '0', 'O', and 'Q' to avoid confusion
# - remove vowels to avoid spelling words
invalid_password_chars = ['a','e','i','o','u','y','l','q']

def getValidPasswordChars():
    password_chars = []
    for i in range(0, 26):
        if chr(ord('a')+i) not in invalid_password_chars:
            password_chars.append(chr(ord('a')+i))
            password_chars.append(chr(ord('A')+i))
    for i in range(2, 10):
        password_chars.append(chr(ord('0')+i))
    return password_chars

password_chars = getValidPasswordChars()


# seed the random number generator
random.seed()


class RegistrationTool( BaseTool ):
    meta_type='CMFMember Registration Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    md5key = None

    def __init__(self):
        if hasattr(BaseTool, '__init__'):
            BaseTool.__init__(self)
        # build and persist an MD5 key
        self.md5key = ''
        for i in range(0, 20):
            self.md5key += chr(ord('a')+random.randint(0,26))
        self._v_md5base = None

    def _md5base(self):
        if self._v_md5base == None:
            self._v_md5base = md5.new(self.md5key)
        return self._v_md5base


    # A replacement for portal_registration's mailPassword function
    # The replacement secures the mail password function with
    # MAIL_PASSWORD_PERMISSION so that members can be disabled.
    security.declarePublic( 'mailPassword' )
    def mailPassword(self, forgotten_userid, REQUEST):
        """
        Email a forgotten password to a member.
        o Raise an exception if user ID is not found.
        """
        membership_tool = getToolByName(self, 'portal_membership')
        member = membership_tool.getMemberById(forgotten_userid)

        if member is None:
            raise 'NotFound', 'The username you entered could not be found.'
            
        # we have to do our own security check since we are in a tool
        # and bypassing Zope security; we can't call member.mailPassword
        # directly since in private state it's not viewable by anonymous
        necessary_roles = PermissionRole.rolesForPermissionOn(MAIL_PASSWORD_PERMISSION ,member)
        for role in getSecurityManager().getUser().getRolesInContext( member ):
            if role in necessary_roles: 
                member.mailPassword()
                return self.mail_password_response(self, REQUEST)
        raise(Unauthorized)

    # Get a password of the prescribed length
    #
    # For s=None, generates a random password
    # For s!=None, generates a deterministic password using a hash of s
    #   (length must be <= 16 for s != None)
    #
    def getPassword(self, length=5, s=None):
        global password_chars, md5base

        if s is None:
            password = ''
            n = len(password_chars)
            for i in range(0,length):
                password += password_chars[random.randint(0,n-1)]
            return password
        else:
            m = self._md5base().copy()
            m.update(s)
            d = m.digest() # compute md5(md5key + s)
            assert(len(d) >= length)
            password = ''
            nchars = len(password_chars)
            for i in range(0, length):
                password += password_chars[ord(d[i]) % nchars]
            return password


    security.declarePublic('generatePassword')
    def generatePassword(self):
        """Generates a password which is guaranteed to comply
        with the password policy."""
        # provide public access to the getPassword methog
        return self.getPassword(6)


    security.declarePrivate('getResetPasswordCode')
    def getResetPasswordCode(self, member_id):
        membership_tool = getToolByName(self, 'portal_membership')
        member = membership_tool.getMemberById(member_id)
        if not member:
            raise KeyError(member_id)
        return self.getPassword(6, member.getPassword())


    def resetPassword(self, member_id, password, code):
        if code != self.getResetPasswordCode(member_id):
            return 0
        membership = getToolByName(self, 'portal_membership')
        member = membership.getMemberById(member_id)
        mapping = {'password':password}

        # if the member has never logged in, set the last_login_time so that
        #   the member is not prompted to change her password when she first
        #   logs in
        if member.login_time == '2000/01/01':
            mapping['login_time'] = DateTime.DateTime()

        self.setMemberProperties(member, mapping)
        return 1

    security.declarePublic( 'registeredNotify' )
    def registeredNotify( self, new_member_id ):

        """ Handle mailing the registration / welcome message.
        """
        ## Duplicated the entire method from CMFDefault.RegistrationTool
        ## only to convert unicode of mail_text to a string... ugh!
        membership = getToolByName( self, 'portal_membership' )
        member = membership.getMemberById( new_member_id )

        if member is None:
            raise 'NotFound', 'The username you entered could not be found.'

        password = member.getPassword()
        email = member.getProperty( 'email' )

        utils = getToolByName(self, 'plone_utils')
        if (not email) or (not utils.validateSingleEmailAddress(email)):
            raise 'ValueError', 'Invalid email address.'
    
        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        mail_text = str(self.registered_notify_template( self
                                                         , self.REQUEST
                                                         , member=member
                                                         , password=password
                                                         , email=email
                                                         ))

        host = self.MailHost
        host.send( mail_text )

        return self.mail_password_response( self, self.REQUEST )

    import re
    __ALLOWED_MEMBER_ID_PATTERN = re.compile( "^[A-Za-z][A-Za-z0-9_]*$" )
    security.declareProtected(ADD_MEMBER_PERMISSION, 'isMemberIdAllowed')
    def isMemberIdAllowed(self, id):
        '''Returns 1 if the ID is not in use and is not reserved.
        '''
        if len(id) < 1 or id == 'Anonymous User':
            return 0
        if not self.__ALLOWED_MEMBER_ID_PATTERN.match( id ):
            return 0
        # Avoid wrapping the user and creating member instance
        memberdata = getToolByName(self, 'portal_memberdata')
        if memberdata.has_key(id):
            return 0
        if self.acl_users.getUserById(id, None) is not None:
            return 0
        return 1



    security.declareProtected(CMFCorePermissions.AddPortalMember, 'isMemberIdAllowed')
    def isMemberIdAllowed(self, userid):
        '''Returns 1 if the ID is not in use and is not reserved.
        '''
        if len(userid) < 1 or id == 'Anonymous User':
            return 0

        site_props = self.portal_properties.site_properties
        pattern = site_props.getProperty('portal_member_validid_re',
                                         "^[A-Za-z][A-Za-z0-9_]*$")
        if not re.match(pattern, userid):
            return 0
        membership = getToolByName(self, 'portal_membership')
        if membership.getMemberById(userid) is not None:
            return 0
        return 1

InitializeClass(RegistrationTool)

