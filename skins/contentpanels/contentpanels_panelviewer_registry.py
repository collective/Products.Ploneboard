## Script (Python) "contentpanels_slots_registry"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

# {portal_type/meta_type:Viewer}

return {
          'Document':'document_panel_view'
        , 'Plone Folder': 'folder_panel_view'
        , 'News Item': 'document_panel_view'
        , 'CMFNeoBoard': 'neoboard_panel_view'
        , 'Topic': 'topic_panel_view'
        , 'NoncmfWrapper': 'noncmfwrapper_panel_view'
        , 'Forum': 'forum_panel_view'
        ,  'CMF BTree Folder':'folder_panel_view'
        ,  'CMF Wiki Page':'cmfwikipage_panel_view'
        , 'ZWiki Page':'cmfwikipage_panel_view'
       }

