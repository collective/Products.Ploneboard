try:
    from lipsum import markupgenerator
except ImportError:
    class markupgenerator(object):
        def __init__(self,sample,dictionary):pass
        def generate_sentence(self):return 'subject'
        def generate_paragraph(self):return 'Please install lorem-ipsum-generator.'

from random import betavariate
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



def lotsofposts(context):

    if not context.readDataFile('ploneboard_lotsofposts.txt'):
        return

    sample = 'This is an example text. It is simple text. Like in school'
    dictionary = 'Python PHP Vignette Java Sun Guido time-travel machine state Lisp Prolog logic Plone release developer Budapest'
    mg = markupgenerator(sample=sample, dictionary=dictionary)

    # XXX CREATE 1000 REAL USERS WITH AVATARS FOR POSTING

    # For every forum, create random content for a total of a configurable number
    count = 100
    site=context.getSite()
    board = site.ploneboard # From the basicboard dependency
    forums = board.getForums()
    for forum in forums:
        i = 0
        while i < count:
            conv = forum.addConversation(mg.generate_sentence(), mg.generate_paragraph())
            i+=1
            # XXX add arbitrary number of comments, which all count towards count
            for j in range(0,int(betavariate(1, 5) * (count/10))):
                if i < count:
                    conv.addComment(mg.generate_sentence(), mg.generate_paragraph())
                    i+=1
                else:
                    continue


