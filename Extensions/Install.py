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

def setupNavigation(p):
    portal_form = getToolByName(p, 'portal_form')
    portal_navigation = getToolByName(p, 'portal_navigation')

    portal_form.setValidators('mpoll_slot' , ['mpoll_validate_vote'])
    portal_form.setValidators('mpoll_poll' , ['mpoll_validate_vote'])
    
    # set up navigation properties
    # Ploneboard
    portal_navigation.addTransitionFor('default',
                                       'mpoll_vote',
                                       'failure',
                                       'action:view')

    portal_navigation.addTransitionFor('default',
                                       'mpoll_vote',
                                       'success',
                                       'action:view')

    portal_navigation.addTransitionFor('default',
                                       'mpoll_slot',
                                       'failure',
                                       'action:view')

    portal_navigation.addTransitionFor('default',
                                       'mpoll_slot',
                                       'success',
                                       'script:mpoll_vote')

    portal_navigation.addTransitionFor('default',
                                       'mpoll_poll',
                                       'success',
                                       'script:mpoll_vote')

    portal_navigation.addTransitionFor('default',
                                       'mpoll_poll',
                                       'failure',
                                       'action:view')

def install(self):
    out = StringIO()

    if not hasattr(self, "_isPortalRoot"):
        print >> out, "Must be installed in a CMF Site (read Plone)"
        return

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME,
                 types_globals)

    setupNavigation(self)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
