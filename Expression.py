"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from Acquisition import aq_inner, aq_parent
from AccessControl import getSecurityManager, ClassSecurityInfo
from Globals import InitializeClass
from Persistence import Persistent
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import SecureModuleImporter


class Expression (Persistent):
    text = ''
    _v_compiled = None

    security = ClassSecurityInfo()

    def __init__(self, text):
        self.text = text
        self._v_compiled = getEngine().compile(text)

    def __call__(self, econtext):
        compiled = self._v_compiled
        if compiled is None:
            compiled = self._v_compiled = getEngine().compile(self.text)
        res = compiled(econtext)
        if isinstance(res, Exception):
            raise res
        return res

InitializeClass(Expression)

def createExprContext(element, ob):
    '''
    An expression context provides names for TALES expressions.
    '''

    data = {
        'here':         ob,
        'container':    aq_parent(aq_inner(ob)),
        'nothing':      None,
        'element':      element,
        'request':      getattr(ob, 'REQUEST', None),
        'modules':      SecureModuleImporter,
        'user':         getSecurityManager().getUser(),
        }
    return getEngine().getContext(data)






