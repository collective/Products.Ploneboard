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

from Products.Archetypes.interfaces.field import IFileField
from Products.Archetypes.debug import log 

CSV='users.csv'
FILE_DIR='user_files'

#from App.config import getConfiguration

#instance_home = getConfiguration().instancehome

import os

import csv

class implog:
    """ a wee log wrapper """
    
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, msg):
        log("%s >> %s\n" %(self.prefix, msg))

class Filer:
    """
    utility filing class
    """

    def __init__(self, filedir, file_fnames, portrait_field=None):
        self.portrait_field=portrait_field
        self.filedir=filedir
        self.fnames=file_fnames
        self.file_list = os.listdir(filedir)
        self.open_files={}

    def user_files(self, username):
        return [ filename for filename in self.file_list if filename.startswith(username) ]

    def close_files(self, username):
        files = self.open_files[username]
        [ file.close() for file in files ]

    def procFiles(self, username):
        ret={}
        filedir=self.filedir
        file_fnames = self.fnames
        user_files = self.user_files(username)
        self.open_files[username]=[]

        pf = [ file for file in user_files if not file.find('_') + 1 ]
        
        if pf:
            user_files.remove( pf[0] )
            if self.portrait_field:
                ret[ self.portrait_field ] = open(os.path.join(filedir, pf[0]), 'r')
                
        ret.update( dict( [ ( file.split('_').pop().split('.')[0], open(os.path.join(filedir, file), 'r') )  for file in user_files ] ) )

        self.open_files[username]=ret.values()
        return ret

def importUsers(self, portal, **kw):

    LOG = implog("CMFMember CSV Import")

    
    if kw.has_key('basedir'):
        basedir = kw['basedir']
    else:
        basedir = os.path.join(INSTANCE_HOME, 'import')

    LOG("import dir: %s" %basedir)

    csvpath = os.path.join(basedir,  CSV)
    
    if not os.path.exists(csvpath):
        raise  Exception, 'File does not exist: %s' % csvfile

    csvfile = open(csvpath ,'r')

    memberdata_tool = getToolByName(portal, 'portal_memberdata')
    wf_tool=getToolByName(portal, 'portal_workflow')
    
    schema = memberdata_tool.getMemberSchema()
    fnames = [ field.getName() for field in schema.filterFields(isMetadata=0) ]

    filedir = os.path.join(basedir, FILE_DIR)
    
    filer = None
    if os.path.exists(filedir):
        file_fnames = [ field.getName() for field in schema.filterFields(isMetadata=0) if IFileField.isImplementedBy(field)]

        portrait_field=None
        if "portrait" in file_fnames:
            portrait_field="portrait"
        else:
            portrait_field = schema.filterFields(isPortrait=0)
            if portrait_field:
                portrait_field=portrait_field[0].getName()

        filer = Filer(filedir, file_fnames, portrait_field)

    users = csv.DictReader(csvfile, fnames)
    for user in users:
        file_dict = None
        if filer:
            user.update(filer.procFiles(user['id']))
        ### DWM make log
        ### add overwrite option
            
        if kw.has_key('overwrite') and hasattr(memberdata_tool, user['id']):
            memberdata_tool.manage_delObjects(user['id'])
            
        try:
            memberdata_tool.invokeFactory('Member', **user)
            member = getattr(memberdata_tool.aq_explicit, user['id']) 
            member._createUser()
            member.processForm()
        
            if wf_tool.getInfoFor(member, 'review_state') == 'new':
                LOG("validation failed: %s" %user['id'])
                wf_tool.doAction(member, 'import_fail')
        except :
            LOG("import failed: %s" %user['id'])


        if filer:
            filer.close_files(user['id'])

    csvfile.close()

# this one isn't finnished!
# or even tested once
### update 
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
