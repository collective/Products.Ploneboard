from Products.Archetypes.public import *
from Products.CompositePage.interfaces import ICompositeElement
from Products.CompositePack.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName
from DocumentTemplate.DT_Util import safe_callable
from Acquisition import aq_base

TARGET = 'target'
VIEWLET = 'viewlet'

class Element(BaseContentMixin):
    """A basic, Archetypes-based Composite Element
    that uses references instead of path, and a dropdown
    for selecting templates
    """
    __implements__ = BaseContent.__implements__ + (ICompositeElement,)
    meta_type = portal_type = archetype_name = 'CompositePack Element'
    global_allow = 0
    
    schema = MinimalSchema + Schema((
        ReferenceField(
        'target',
        vocabulary='_get_targets',
        relationship=TARGET,
        #allowed_types=('Document',), # XXX Fix here
        widget=ReferenceWidget(label='Target Object',
                               description=('The object to be displayed '
                                            'when rendering the viewlet.'))
        ),
        ReferenceField(
        'viewlet',
        #vocabulary='_get_viewlets',
        relationship=VIEWLET,
        #allowed_types=('CompositePack Viewlet',),
        widget=ReferenceWidget(label='Viewlet',
                               description=('The viewlet to be used '
                                            'for rendering the '
                                            'Context Object'))
        )))

    def _get_targets(self):
        return DisplayList((('test', 'test'),))

    def _get_viewlets(self):
        obj = self.dereference()
        tool = getToolByName(self, 'composite_tool')
        v = tool.getViewletsFor(obj)
        if v is None:
            return DisplayList()
        viewlets = filter(None, (v.get('default'),) + tuple(v.get('viewlets')))
        options = tuple([(i['viewlet'].UID(), i['title'])
                   for i in viewlets])
        return DisplayList(options)

    def template(self):
        """ Returns the template referenced by this composite element.
        """
        refs = self.getRefs(VIEWLET)
        viewlet = refs and refs[0] or None
        if viewlet is None:
            obj = self.dereference()
            tool = getToolByName(self, 'composite_tool')
            viewlets = tool.getViewletsFor(obj)
            if viewlets is None:
                return None
            else:
                viewlet = viewlets.get('default')['viewlet']
        return viewlet and viewlet.getTemplate() or viewlet

    # ICompositeElement implementation
    def dereference(self):
        """Returns the object referenced by this composite element.
        """
        refs = self.getRefs(TARGET)
        return refs and refs[0] or None

    def renderInline(self):
        """Returns a representation of this object as a string.
        """
        obj = self.dereference()
        template = self.template()
        if template is not None:
            if obj is not None:
                # Rewrap the template to give it the right context
                template = aq_base(template).__of__(obj)
            return template()
        # No viewlet, try to call the object
        if safe_callable(obj):
            return obj()
        return str(obj)

    def queryInlineTemplate(self, slot_class_name=None):
        """Returns the name of the inline template this object uses.
        """
        # XXX What does this do?
        return 'Viewlet'

    def setInlineTemplate(self, template):
        """Sets the inline template for this object.
        """
        # XXX What does this do?
        return 'Viewlet'

    def listAllowableInlineTemplates(self, slot_class_name=None):
        """Returns a list of inline template names allowable for this object.
        """
        tool = getToolByName(self, 'composite_tool', None)
        if tool is not None:
            obj = self.dereference()
            viewlets = tool.getViewletsFor(obj)
            return [(i['id'], i['title']) for i in viewlets]
        # No tool found, so no inline templates are known.
        return ()

registerType(Element, PROJECTNAME)
