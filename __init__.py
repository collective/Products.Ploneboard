__version__ = '''
$Id: __init__.py,v 1.1 2003/01/02 15:29:12 lalo Exp $
'''.strip()

from PlacelessTranslationService import PlacelessTranslationService
from GettextMessageCatalog import GettextMessageCatalog
from Products.PageTemplates.GlobalTranslationService import setGlobalTranslationService
import os, glob, zLOG, sys


# default (gettext) translation service
translation_service = PlacelessTranslationService('default')
# set the translation service
setGlobalTranslationService(translation_service)

# sweep the i18n directory
basepath = os.path.join(INSTANCE_HOME, 'i18n')
if os.path.isdir(basepath):
    names = glob.glob(os.path.join(basepath, '*.mo'))
    if not names:
        print 'no translations found!'
    for name in names:
        try:
            translation_service.addCatalog(GettextMessageCatalog(name))
        except ValueError:
            zLOG.LOG('AltPTi18n', zLOG.PROBLEM, 'Message Catalog has no metadata',
                     name, sys.exc_info())
        except:
            zLOG.LOG('AltPTi18n', zLOG.PROBLEM, 'Message Catalog has errors',
                     name, sys.exc_info())

def initialize(context):
    pass
