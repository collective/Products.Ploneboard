
###########################################################
###
### DEFAULT VIEWLETS TABLE
### 
### viewlet are content related portlets. it can be a zpt 
### macro or any other(ZPTlet or Script(python)...) 
###
### 1. Every viewlet is a CMF action in portal_contentpanels.
###    So you have all the feature action have...
###
### 2. the follow viewlet actions are:
###
###    id, name, url, condition, permision, category, visible
###
### 3. be careful to the catagory's prefix:
###    
###    - PT: content specific viewlets.
###      it should be PT:PotalTypeID
###
###    - GL: context sensitive viewlets
###        not content specific, but sensitive with its context 
###
###      GL:folder     all folderish content specific
###      GL:content    all non-folderish content specific
###      GL:all        all content specific
###
###    - GN: general portlets. they are not context sensitive
###
###      GN:portal     site-wide viewlets
###      GN:personal   personal related viewlets
###
###########################################################

actions=[

### PT: portal type specific viewlets

('document_viewlet', 'Body', 
"string: here/viewlet_document_body/macros/portlet",
'', "View","PT:Document",1),

('view_viewlet', 'Body',
'string: here/viewlets_topic_list/macros/base_portlet', 
'', 'View', 'PT:Topic', 1),

('topic_title_only', 'title only',
'string: here/viewlets_topic_list/macros/title_only',
'', 'View', 'PT:Topic', 1),

('image_view','Body',
'string:here/viewlet_image_body/macros/portlet',
"","View","PT:Image", 1),

("wiki_page_content","Body",
"string:here/viewlet_zwikipage_body/macros/portlet",
"","View","PT:Wiki Page",1),

('contentpanels_viewlet', 'Nested ContentPanels', 
'string:here/viewlet_contentpanels_body/macros/portlet', 
'', 'View','PT:ContentPanels', 1),

('plonechat_viewlet', 'recent messages',
'string:here/viewlet_plonechat_body/macros/portlet',
'', 'View','PT:PloneChat', 1),

('viewlet_dynamicpage', 'dynamic page',
'string:here/viewlet_dynamicpage/macros/portlet',
'', 'View', 'PT:Dynamic Page', 1),

### GL: global viewlets

('default_viewlet', 'Default Viewlet',
'string:here/viewlet_default/macros/portlet',
'', 'View', 'GL:all', 1),

('latest_updates_viewlet', 'Recent Updates',
'string:here/viewlets_folder_recent/macros/base_portlet',
'', 'View', 'GL:folder',1 ),

('folder_list_viewlet' , 'Folder Listing',
'string:here/viewlets_folder_listing/macros/base_portlet', 
'', 'View', 'GL:folder', 1),

('portlet_calendar', 'Calendar', 
'string:here/portlet_calendar/macros/portlet',
'', 'View', 'GL:folder', 1),

('portlet_events', 'Events', 
'string:here/portlet_events/macros/portlet',
'', 'View', 'GL:folder', 1),

('portlet_review', 'Review List', 
'string:here/portlet_review/macros/portlet',
'', 'Review portal content', 'GL:folder', 1),

('portlet_news', 'News', 
'string:here/portlet_news/macros/portlet', 
'', 'View', 'GL:folder', 1),

('portlet_recent', 'Recent Published',
'string:here/portlet_recent/macros/portlet',
'', 'View', 'GL:folder', 1),

### global portlet

('portlet_language', 'Language',
'string:here/portlet_language/macros/portlet',
'', 'View', 'GN:portal', 1),

('my_recent_changes', 'My Recent Updates',
'string:here/portlet_mychanges/macros/portlet',
'', 'View', 'GN:personal', 1),

('portlet_favorites', 'My Favorites',
'string:here/portlet_favorites/macros/portlet',
'', 'View', 'GN:personal', 1),

###
]
