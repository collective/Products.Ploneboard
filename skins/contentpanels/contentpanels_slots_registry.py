## Script (Python) "contentpanels_slot_registry"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

# {solt_name:slot_url}

return [
          ('None', 'here/contentpanels_NoBorderNoTitleSkin/macros/skinslot')
        , ('Title Only', 'here/contentpanels_NoBorderWithTitleSkin/macros/skinslot')
	, ('Plone Box', 'here/contentpanels_PloneSlotSkin/macros/skinslot')
        , ('Blue Box', 'here/contentpanels_BlueBoxSkin/macros/skinslot')
        , ('Yellow Box', 'here/contentpanels_YellowBoxSkin/macros/skinslot')
	, ('Red Box',  'here/contentpanels_RedBoxSkin/macros/skinslot')
        , ('What is New', 'here/whatsnew_slot/macros/whatsnewBox')
        , ('About Box', 'here/about_slot/macros/aboutBox')
        , ('Related Box', 'here/related_slot/macros/relatedBox')
        , ('Calendar', 'here/calendar_slot/macros/calendarBox')
        , ('latest Event', 'here/events_slot/macros/eventsBox')
        , ('Navigation Tree', 'here/navigation_tree_slot/macros/navigationBox')
        , ('News Box', 'here/news_slot/macros/newsBox')
        , ('Review Box', 'here/workflow_review_slot/macros/review_box')
        , ('My Slot', 'here/my_slot/macros/myslotBox')
       ]
