from Products.CMFCore.utils import getToolByName
from Products.Ploneboard.config import EMOTICON_TRANSFORM_MODULE
from Products.Ploneboard.config import URL_TRANSFORM_MODULE
from Products.Ploneboard.config import SAFE_HTML_TRANSFORM_MODULE

def setupVarious(context):
    
    if not context.readDataFile('ploneboard_various.txt'):
        return
    
    site=context.getSite()
    addTransforms(site)
    setupCommentLocalRoles(site)
    addPlacefulPolicy(site)


def addTransforms(site):
    pb_tool = getToolByName(site, 'portal_ploneboard')
    pb_tool.registerTransform('text_to_emoticons', EMOTICON_TRANSFORM_MODULE, 'Graphical smilies')
    pb_tool.registerTransform('url_to_hyperlink', URL_TRANSFORM_MODULE, 'Clickable links')
    pb_tool.registerTransform('safe_html', SAFE_HTML_TRANSFORM_MODULE, 'Remove dangerous HTML')

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
