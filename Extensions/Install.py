from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes import listTypes
from Products.CMFCore.utils import getToolByName
from Products.MPoll.config import *
from Products.MPoll import types_globals

from StringIO import StringIO

def changeVisibility(p, portal_type, action, value):
    """
    Change the action of a type.
    """
    tt=getToolByName(p, 'portal_types')
    actions=tt[portal_type]._cloneActions()
    for a in actions:
        try:
           if a.get('id','') in (action, ): 
              a['visible']=value
        except:
           if a.id in (action, ):
              a.visible=value
    tt[portal_type]._actions=actions

def install(self):
    out = StringIO()

    if not hasattr(self, "_isPortalRoot"):
        print >> out, "Must be installed in a CMF Site (read Plone)"
        return

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME,
                 types_globals)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
