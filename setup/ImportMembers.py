from OFS.PropertyManager import PropertyManager
from Products.CMFMember.Extensions.Workflow import triggerAutomaticTransitions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFPlone.migrations.migration_util import safeEditProperty
from Acquisition import aq_get

from Products.SiteErrorLog.SiteErrorLog import manage_addErrorLog

from cStringIO import StringIO

from zLOG import INFO, ERROR
from Products.CMFPlone.setup.SetupBase import SetupWidget

def importUsers(self, portal):
    # requirements
    # file : /tmp/users.csv
    # portraits if any : /tmp/images/ 
    import string
    memberdata_tool = getToolByName(portal, 'portal_memberdata')
    wf_tool=getToolByName(portal, 'portal_workflow')
    import codecs
    users = codecs.open('/tmp/users.csv','r','utf-8').readlines()
    for user in users:
        try:
            (username,password,email,fullname,imageName) = string.split(user, ',')
        except:
            return user
        # check if the imageName from csv file isn't empty or default spacer.gif
        if ( imageName and imageName != 'Images/spacer.gif'):
            imageName='/tmp/images/%s' % imageName
            try:
                image = open(imageName,'r')
            except:
                # we didn't get any image, filepath in csv can be wrong
                # or the file doesn't exist
                image = None
        else:
            image = None
        try:
            memberdata_tool.invokeFactory('Member', username)
            member = getattr(memberdata_tool.aq_explicit, username) 
            member.update(**{'password':password,'roles':('Member',),'domains':(),'confirm_password':password,'fullname':fullname,'email':email,'portrait':image}) 
            member._createUser()
            member.processForm() 
            if(image):
                image.close()
        except:
            pass
               
       
        
   

# this one isn't finnished!
# or even tested once
def importFromUploadeCSV(self, portal, **kwargs):
    import string
    memberdata_tool = getToolByName(portal, 'portal_memberdata')

    import codecs
    file = codecs.open(kwargs['csvfile'],'r',kwargs['charset'])
    #first line contains field names
    fields = file.readline()
    fields = string.replace(fields,'\"','')
    users = file.readlines()
    for user in users:
        try:
            # create a dict from fields and user variables
            memberInfo = dict(zip(fields, user))
        except:
            # if we get an error return where in the file
            raise 'Error', user
        
        try:
            memberdata_tool.invokeFactory(kwargs['membertype'], memberInfo['username'])
            member = getattr(memberdata_tool.aq_explicit, memberInfo['username'])
            member.edit(password=memberInfo['password'],roles=('Member',),domains=(),**memberInfo)
        except:
            pass
    
functions = {
    'Import from CSV':importUsers
    }


class ImportSetup(SetupWidget):
    type = 'CMFMember Import Setup'

    description = """CMFMember importing users"""

    configlets = (
    {'id':'cmfmemberImportCSV',
     'appId':'CMFMember',
     'name':'CMFMember Import from CSV',
     'action':'string:${portal_url}/cmfmember_control/prefs_cmfmember_import',
     'category':'CMFMember',
     'permission': CMFCorePermissions.ManagePortal,
     'imageUrl':'group.gif'},
    )

    def setup(self):
        pass

    def delItems(self, fns):
        out = []
        out.append(('Currently there is no way to remove a function', INFO))
        return out

    def run(self, fn, **kwargs):
        out = []
        out.append((functions[fn](self, self.portal, **kwargs),INFO))
        out.append(('Function %s has been applied' % fn, INFO))
        return out

    def addItems(self, fns):
        out = []
        for fn in fns:
            out.append((functions[fn](self, self.portal),INFO))
            out.append(('Function %s has been applied' % fn, INFO))
        return out

    def installed(self):
        return []

    def available(self):
        """ Go get the functions """
        return functions.keys()
