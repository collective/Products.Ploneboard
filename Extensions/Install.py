from Products.CMFMetadata.MetadataTool import MetadataTool

def install(self):
    portal = self.portal_url.getPortalObject()
    portal._setObject(MetadataTool.id, MetadataTool())

    return 'CMF Advanced Metadata Tool Installed'
