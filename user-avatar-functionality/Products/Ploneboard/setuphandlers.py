from Products.CMFCore.utils import getToolByName
from Products.Ploneboard.config import EMOTICON_TRANSFORM_MODULE
from Products.Ploneboard.config import URL_TRANSFORM_MODULE
from Products.Ploneboard.config import SAFE_HTML_TRANSFORM_MODULE

def setupVarious(context):
    
    if not context.readDataFile('ploneboard_various.txt'):
        return
    
    site=context.getSite()
    addTransforms(site)


def addTransforms(site):
    pb_tool = getToolByName(site, 'portal_ploneboard')
    pb_tool.registerTransform('text_to_emoticons', EMOTICON_TRANSFORM_MODULE, 'Graphical smilies')
    pb_tool.registerTransform('url_to_hyperlink', URL_TRANSFORM_MODULE, 'Clickable links')
    pb_tool.registerTransform('safe_html', SAFE_HTML_TRANSFORM_MODULE, 'Remove dangerous HTML')

