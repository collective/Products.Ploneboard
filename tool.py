import os

import Globals
from Globals import PersistentMapping, Persistent

from AccessControl import ClassSecurityInfo

from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import getToolByName

from Products.CompositePage.tool import CompositeTool as BaseTool
from Products.CompositePack.config import TOOL_ID, LAYOUTS

zmi_dir = os.path.join(Globals.package_home(globals()),'www')

DEFAULT = '(Default)'

class CompositeTool(Folder, BaseTool):
    """ CompositePack Tool """

    # XXX id = 'portal_composite'
    id = TOOL_ID
    meta_type = 'CompositePack Tool'

    security = ClassSecurityInfo()

    manage_options = (Folder.manage_options[:1] +
                      ({'label' : 'Viewlets',
                        'action' : 'manage_selectViewlets' },) +
                      Folder.manage_options[1:])

    _viewlets_by_type = None # PersistentMapping
    _default_viewlets = ('default_viewlet', 'link_viewlet')
    _default_default = 'default_viewlet'
    
    #def __init__(self):
    #    self.id = TOOL_ID
      
    def __repr__(self):
        return "CompositePack Tool"

    security.declareProtected( ManagePortal, 'manage_selectViewlets')
    def manage_selectViewlets(self, REQUEST, manage_tabs_message=None):
        '''Manage association between types and viewlets.
        '''
        vbt = self._viewlets_by_type
        ti = self._listTypeInfo()
        types_info = []
        # Viewlet IDs. All viewlets are available for
        # all content types for now, but this may change in the
        # future.
        viewlet_info = [{'id':ob.getId(), 'title':ob.title_or_id()}
                        for ob in self.viewlets.objectValues()]
        viewlet_info.sort(lambda x, y: cmp(x['title'], y['title']))
        available_viewlets = viewlet_info[:]
        viewlet_info.insert(0, {'id':DEFAULT, 'title':'Default'})
        for t in ti:
            id = t.getId()
            title = t.Title()
            if title == id:
                title = None
            if vbt is not None and vbt.has_key(id):
                viewlets = vbt[id].viewlets
                default_per_type = vbt[id].default
            else:
                viewlets = (DEFAULT,)
                default_per_type = DEFAULT
            types_info.append({'id': id,
                               'title': title,
                               'viewlets': viewlets,
                               'default':default_per_type,
                               'viewlet_info':viewlet_info})

        return self._manage_selectViewlets(
            REQUEST, default_viewlets=self._default_viewlets,
            default_default=self._default_default,
            types_info=types_info,
            available_viewlets=available_viewlets)

    _manage_selectViewlets = PageTemplateFile('selectViewlets.pt',
        zmi_dir)

    security.declareProtected( ManagePortal, 'manage_changeViewlets')
    def manage_changeViewlets(self, default_viewlets, default_default, \
                              props=None, REQUEST=None):
        """ Changes which viewlets apply to objects of which type.
        """
        if props is None:
            props = REQUEST
        # Set up the default viewlets.
        ids = []
        for viewlet_id in default_viewlets:
            if viewlet_id:
                if not self.getViewletById(viewlet_id):
                    raise ValueError, (
                        '"%s" is not a viewlet ID.' % viewlet_id)
                ids.append(viewlet_id)
        if default_default not in default_viewlets:
            raise ValueError, ('For Default, the default '
                               'viewlet (%s) is not among '
                               'viewlets (%s).' % (default_default,
                                                   default_viewlets))
        self._default_viewlets = tuple(ids)
        self._default_default = default_default
        vbt = self._viewlets_by_type
        if vbt is None:
            self._viewlets_by_type = vbt = PersistentMapping()
        ti = self._listTypeInfo()
        # Set up the viewlets by type.
        for t in ti:
            id = t.getId()
            field_name = 'viewlets_%s' % id
            viewlets = tuple(props.get(field_name, (DEFAULT,)))
            field_name = 'default_%s' % id
            default = props.get(field_name, DEFAULT).strip()
            if viewlets == (DEFAULT,) and default == DEFAULT:
                # Remove from vbt.
                if vbt.has_key(id):
                    del vbt[id]
            else:
                viewlets = filter(lambda x: x != DEFAULT, viewlets)
                ids = []
                for viewlet_id in viewlets:
                    if viewlet_id:
                        if not self.getViewletById(viewlet_id):
                            raise ValueError, ('"%s" is not a '
                                               'registered viewlet.' %
                                               viewlet_id)
                        ids.append(viewlet_id)
                if default == DEFAULT:
                    if self._default_default not in viewlets:
                        raise ValueError, (
                            'For type %s, the default viewlet (%s) '
                            'is not among viewlets '
                            '(%s).' % (id, self._default_default, viewlets))
                elif not ((not viewlets and
                           default in self._default_viewlets) or
                          default in viewlets):
                    if not viewlets:
                        viewlets = self._default_viewlets
                    raise ValueError, (
                        'For type %s, the default viewlet '
                        '(%s) is not among viewlets '
                        '(%s).' % (id, default, viewlets))
                vft = ViewletsForType()
                if not ids:
                    ids = (DEFAULT,)
                vft.viewlets = tuple(ids)
                vft.default = default
                vbt[id] = vft
        if REQUEST is not None:
            return self.manage_selectViewlets(REQUEST,
                            manage_tabs_message='Changed.')

    security.declarePrivate( '_listTypeInfo' )
    def _listTypeInfo(self):
        """ List the portal types which are available.
        """
        pt = getToolByName(self, 'portal_types', None)
        if pt is None:
            return ()
        else:
            return pt.listTypeInfo()

    def getViewletById(self, id):
        if hasattr(self.viewlets, id):
            return getattr(self.viewlets, id)
        else:
            return None

    def getViewletsFor(self, obj=None):
        """ Get viewlets for a given object """
        type_id = None
        if obj is not None:
            type_id = obj.getTypeInfo().getId()
        return self.getViewletsForType(type_id)

    def getViewletsForType(self, portal_type=None):
        """ Get viewlets for a given type

        Return a dict where:

          - 'default' value is the default viewlet struct
          - 'viewlets' value is a list of structs with
            the other viewlets

        Each struct is composed of:

          - Viewlet id
          - Viewlet title
          - Viewlet object

        May return None.
        """
        vbt = self._viewlets_by_type
        if vbt is not None:
            info = vbt.get(portal_type)
            if info is None:
                # Return default viewlets
                default = self._default_default
                viewlets = self._default_viewlets
            else:
                default = info.default
                if default == DEFAULT:
                    default = self._default_default
                viewlets = info.viewlets
                if viewlets == DEFAULT:
                    viewlets = self._default_viewlets
        else:            
            # Return default viewlets
            default = self._default_default
            viewlets = self._default_viewlets
        v_names = tuple(viewlets) + (default,)
        v_names = filter(lambda x: x != DEFAULT, v_names)
        viewlets = {}
        for name in v_names:
            viewlet = self.getViewletById(name)
            if viewlet is None:
                continue
            viewlets[name] = {'id':name,
                              'title':viewlet.title_or_id(),
                              'viewlet':viewlet
                              }
        if not viewlets:
            return None
        viewlets_info = viewlets.values()
        if viewlets.has_key(default):
            default_viewlet = viewlets[default]
            del viewlets[default]
            viewlets_info = viewlets.values()
        else:
            default_viewlet = viewlets_info.pop()
        return {'default':default_viewlet, 'viewlets':viewlets_info}

    def findSnippets(self, **kwargs):
        """ Find snippets for use as Composite Element targets

        Those can include:
           - Filesystem Composite Snippets
           - Registered Viewlets

        In the case where a 'context' keyword argument is passed,
        the viewlets returned are only those that apply to the context.
        """
        st = getToolByName(self, 'portal_skins')
        ct = getToolByName(self, 'portal_catalog')
        f_params = {'search_sub':1}
        c_params = {'portal_type':'CompositePack Viewlet'}
        mt = kwargs.get('meta_type')
        if mt is not None:
            f_params['obj_metatypes'] = mt
        else:
            f_params['obj_metatypes'] = ['Filesystem Composite Snippet']
        text = kwargs.get('SearchableText')
        if mt is not None:
            f_params['obj_searchterm'] = text
            c_params['SearchableText'] = text
        f_res = st.ZopeFind(st, **f_params)
        s_res = ct(**c_params)
        context = kwargs.get('context')
        if context is not None:
            v_info = self.getViewletsFor(context)
            if v_info is not None:
                v_info = v_info.get('default', ()) + v_info.get('viewlets', ())
                v_ids = [v['id'] for v in v_info]
                s_res = filter(lambda b: b.id in v_ids, s_res)
        result = [t for p, t in f_res]
        templates = [b.getObject().getTemplate() for b in s_res]
        result.extend(templates)
        return templates

class ViewletsForType(Persistent):
    def __init__(self):
        self.viewlets  = ()
        self.default = ''

Globals.InitializeClass(CompositeTool)

def manage_addCompositeTool(dispatcher, REQUEST=None):
    """Adds a composite tool to a folder.
    """
    from Products.CompositePack.viewlet import container
    from Products.CompositePack import viewlet
    from Products.CompositePack.config import VIEWLETS, LAYOUTS
    ob = CompositeTool()
    dispatcher._setObject(ob.getId(), ob)
    ob = dispatcher._getOb(ob.getId())
    container.addViewletContainer(ob, id=VIEWLETS,
                                  title='A Container for registered Viewlets')
    container.addViewletContainer(ob, id=LAYOUTS,
                                  title='A Container for registered Layouts')
    layouts = getattr(ob, LAYOUTS)
    viewlet.addViewlet(layouts, 
                       id='two_slots', 
                       title='Two slots', 
                       template_path='portal_skins/compositepack/two_slots'
                       )
    viewlet.addViewlet(layouts, 
                       id='three_slots', 
                       title='Three slots', 
                       template_path='portal_skins/compositepack/three_slots')
    viewlets = getattr(ob, VIEWLETS)
    viewlet.addViewlet(viewlets, 
                       id='default_viewlet', 
                       title='Default viewlet', 
                       template_path='default_viewlet')
    viewlet.addViewlet(viewlets, 
                       id='link_viewlet', 
                       title='Link Only', 
                       template_path='link_viewlet')
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST)
