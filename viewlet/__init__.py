from Products.Archetypes.public import *
from Products.CompositePack.viewlet.interfaces import IViewlet
from Products.CompositePack.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName

class Viewlet(BaseContentMixin):
    """A basic, Archetypes-based Composite Element
    that uses references instead of path, and a dropdown
    for selecting templates
    """

    __implements__ = BaseContent.__implements__ + (IViewlet,)

    meta_type = portal_type = archetype_name = 'CompositePack Viewlet'
    global_allow = 0

    schema = MinimalSchema + Schema((
        StringField(
        'template_path',
        widget=StringWidget(label='Template Path',
                            description=('Path to the template to '
                                         'be used for rendering '
                                         'the viewlet.'))
        ),
        ))


    def getTemplate(self):
        """ Return the template """
        purl = getToolByName(self, 'portal_url')
        portal = purl.getPortalObject()
        return portal.restrictedTraverse(self.getTemplate_path())

registerType(Viewlet, PROJECTNAME)
