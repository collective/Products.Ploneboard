try:
    from lipsum import markupgenerator
except ImportError:
    class markupgenerator(object):
        def __init__(self,sample,dictionary):pass
        def generate_sentence(self):return 'subject'
        def generate_paragraph(self):return 'Please install lorem-ipsum-generator.'

import transaction
from time import time
from random import betavariate
from Products.CMFCore.utils import getToolByName

from Products.SimpleAttachment.setuphandlers import registerAttachmentsFormControllerActions, registerImagesFormControllerActions

from Products.Ploneboard.config import EMOTICON_TRANSFORM_MODULE
from Products.Ploneboard.config import URL_TRANSFORM_MODULE
from Products.Ploneboard.config import SAFE_HTML_TRANSFORM_MODULE

def setupVarious(context):
    
    if not context.readDataFile('ploneboard_various.txt'):
        return
    
    site=context.getSite()
    addCatalogIndexesAndMetadata(site)
    addTransforms(site)
    setupCommentLocalRoles(site)
    addPlacefulPolicy(site)
    setupComment(site)

def addCatalogIndexesAndMetadata(site):
    catalog = getToolByName(site, 'portal_catalog')
    indexes = catalog.indexes()
    schema = catalog.schema()

    data = (('num_comments', 'FieldIndex', True),)
    for name,indextype,metadata in data:
        if indextype and name not in indexes:
            catalog.addIndex(name, indextype)
        if metadata and name not in schema:
            catalog.addColumn(name)

def addTransforms(site):
    pb_tool = getToolByName(site, 'portal_ploneboard')
    pb_tool.registerTransform('text_to_emoticons', EMOTICON_TRANSFORM_MODULE, 'Graphical smilies')
    pb_tool.registerTransform('url_to_hyperlink', URL_TRANSFORM_MODULE, 'Clickable links')
    pb_tool.registerTransform('safe_html', SAFE_HTML_TRANSFORM_MODULE, 'Remove dangerous HTML')

def lotsofposts(context):
    debug = True

    if not context.readDataFile('ploneboard_lotsofposts.txt'):
        return

    sample = context.readDataFile('rabbit.txt')
    dictionary = context.readDataFile('vocab.txt')
    mg = markupgenerator(sample=sample, dictionary=dictionary)

    # XXX CREATE 1000 REAL USERS WITH AVATARS FOR POSTING

    # For every forum, create random content for a total of a configurable number
    totalgoal = 100000
    site=context.getSite()
    board = site.ploneboard # From the basicboard dependency
    forums = board.getForums()
    for forum in forums:
        count = int(totalgoal * betavariate(1, len(forums)-1))
        i = 0
        while i < count:
            start = time()
            conv = forum.addConversation(mg.generate_sentence(), mg.generate_paragraph())
            i+=1
            if debug:
                print "Creating conversation %s of %s in %s in %.5fs" % (i, count, forum.getId(), time()-start)
            if i % 1000 == 0:
                transaction.get().savepoint(optimistic=True)
                if debug:
                    print "\nSAVEPOINT\n"
            # XXX add arbitrary number of comments, which all count towards count
            for j in range(0,int(betavariate(1, 5) * max(300,(count/10)))):
                if i < count:
                    start = time()
                    conv.addComment(mg.generate_sentence(), mg.generate_paragraph())
                    i+=1
                    if debug:
                        print "Creating comment      %s of %s in %s in %.5fs" % (i, count, forum.getId(), time()-start)
                    if i % 1000 == 0:
                        transaction.get().savepoint(optimistic=True)
                        if debug:
                            print "\nSAVEPOINT\n"
                else:
                    continue

def setupCommentLocalRoles(self):
    pc=getToolByName(self, 'portal_catalog')
    pu=getToolByName(self, 'plone_utils')
    comments=pc(object_provides='Products.Ploneboard.interfaces.IComment')
    comments=[x.getObject() for x in comments if x.getObject()]
    count=0
    for c in comments:
        # Do not update needlessly. Screws up modified
        if not pu.isLocalRoleAcquired(c):
            pu.acquireLocalRoles(c, 0)
            count += 1
    self.plone_log('setupCommentLocalRoles', 'Updated %d of total %d comments' % (count, len(comments)))

def addPlacefulPolicy(self):
    pw=getToolByName(self, 'portal_placeful_workflow')
    new_id = 'EditableComment'
    if new_id not in pw.objectIds():
        pw.manage_addWorkflowPolicy(new_id)
        ob = pw[new_id]
        ob.setChain('PloneboardComment', 'ploneboard_editable_comment_workflow')

def cleanupKupuResources(site):
    #cleanup types from kupu resources
    kupuTool = getToolByName(site, 'kupu_library_tool', None)
    if kupuTool:
        resource = 'linkable' 
        ploneboard_types = ["Ploneboard", "PloneboardForum", "PloneboardComment", "PloneboardConversation"]
        resitems = list(kupuTool.getPortalTypesForResourceType(resource))
        items = [ri for ri in resitems if not ri in ploneboard_types]
        kupuTool.updateResourceTypes((
            {'resource_type' : resource,
             'old_type'      : resource,
             'portal_types'  : items},))

def setupComment(site):
    # Set up form controller actions for the widgets to work
    registerAttachmentsFormControllerActions(site, contentType = 'PloneboardComment', template = 'base_edit')
    registerImagesFormControllerActions(site, contentType = 'PloneboardComment', template = 'base_edit')
    # Register form controller actions for LinguaPlone translate_item
    registerAttachmentsFormControllerActions(site, contentType = 'PloneboardComment', template = 'translate_item')
    registerImagesFormControllerActions(site, contentType = 'PloneboardComment', template = 'translate_item')
    site.plone_log('setupComment', 'Updated Widget Attachment Management')

def uninstallVarious(self):
    if self.readDataFile('Products.Ploneboard-uninstall.txt') is None:
        return
    site = self.getSite()
    cleanupKupuResources(site)
