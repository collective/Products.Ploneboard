from Products.CMFCore import utils
from Products.CMFDefault import Portal
import ContentPanels
import Products.CMFCore

from Products.CMFCore import utils, CMFCorePermissions
from Products.CMFCore.DirectoryView import registerDirectory

import sys
this_module = sys.modules[ __name__ ]

factory_type_information = (
    (ContentPanels.factory_type_information
     
     )
    )

contentClasses = (ContentPanels.ContentPanels, )
contentConstructors = (ContentPanels.addContentPanels,)

# This is used by a script (external method) that can be run
# to set up collector in an existing CMF Site instance.
ContentPanels_globals = globals()

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())
registerDirectory('skins/contentpanels', globals())
#registerDirectory('skins/contentpanels/content_views', globals())
#registerDirectory('skins/contentpanels/panel_slots', globals())

def initialize(context):

    utils.ContentInit( 'Content Panels'
                     , content_types=contentClasses
                     , permission=CMFCorePermissions.AddPortalContent
                     , extra_constructors=contentConstructors
                     , fti=factory_type_information
                     ).initialize( context )
