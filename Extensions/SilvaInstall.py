from Products.SilvaMetadata.MetadataTool import MetadataTool
from Products.SilvaMetadata.utils import StringBuffer

def install(self):

    out = StringBuffer()

    print >> out, "Installing Silva Metadata Service"

    silva_id = 'service_metadata'
    root = self.get_root()
    ob = MetadataTool()
    ob.id = silva_id
    root._setObject(silva_id, ob)

    print >> out, "Installation Complete"
    return out.getvalue()

