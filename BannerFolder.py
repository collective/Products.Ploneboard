from Products.Archetypes.public import *
from Products.CMFCore.CMFCorePermissions import ListFolderContents
from Products.CMFCore.utils import getToolByName, getActionContext
from config import PROJECTNAME
import random

class BannerFolder(BaseFolder):
    """A container for Banners"""

    meta_type = 'BannerFolder'
    archetype_name = 'Banner Folder'
    schema = BaseFolder.schema
    allowed_content_types = ['BannerImage']
    immediate_view = 'folder_contents'
    content_icon = 'bannerfolder_icon.gif'

    # TODO: keyword matching algorithm
    # - if there are banners with matching keywords, use one of them
    # - otherwise, use any banner
    def getBanner(self):
        """Get a random BannerImage object from this BannerFolder"""

        wf_tool = getToolByName(self, 'portal_workflow')
        available = []
        for b in self.objectValues(['BannerImage']):
            if wf_tool.getInfoFor(b, 'review_state', None) != 'published': continue
            if b.effective().isFuture(): continue
            if b.expires().isPast(): continue
            if b.getMaxViews() > 0 and b.getViews() >= b.getMaxViews():
                continue
            if b.getMaxClicks() > 0 and b.getClicks() >= b.getMaxClicks():
                continue
            for i in range(b.getWeight()):
                available.append(b)
        if len(available) > 0:
            return random.choice(available)
        else:
            return None

    def folder_contents(self, **kw):
        """List the contents of this BannerFolder"""
        return self.bannerfolder_contents(**kw)

registerType(BannerFolder, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'references'):
            a['condition'] = 'nothing'
    return fti
