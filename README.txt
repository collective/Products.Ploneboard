What is CMFContentPanels?

  CMFContentPanels is a plone portlets product to build composite pages. You can create new content which is composed of other contents as configurable 'content panels'.  You can change the layout, the panel skin and the content viewlet through the web.

 <a
href="http://www.plone.org/Members/panjunyong/ContentPanels/ContentPanels.JPG"
target="_blank">screen shot</a> 

Features

  * support multi-page and mulit-column

  * full function layout management, easy to use: move panels left/right/up/down

  * construction of very complex page: contentpanels can be nested within
    another contentpanels.

  * extensible css panel skin. 4 skins provided by default. Select or extend
    the skin as you like.

  * plone portlet compatible viewlets. easy to extend. 

  * integrate with plone's default portlets, add some new portlet like 'my recent changes'.

  * predefined viewlets for Document, Image, Folder, Topic, ZWiki Page, PloneChat, mxmDynamicPage.

  * suport relative content path

  * contentpanels content can be a plone portlet and show on the left/right column.

How to Use it?

  1. Install it. See INSTALL.txt for more information.

  2. "a howto with
screenshots":http://www.plone.org/Members/panjunyong/ContentPanels/howto

How to Extend CMFContentPanels? (For Developers)

 How to make more viewlets?

  Viewlet is a view of content which can be selected in contentpanels. Viewlet
can be a zpt or a zpt macro. Viewlets are registered with CMF Action
mechanism.

  1. Write a viewlet for your content.  Viewlet structure is the same to 
    "Plone 2 portlet":http://plone.org/Members/arnia/plone2-css-reference/Portlets/wikipage_view.
You can refer to stuff at \CMFContentPanels\skins\contentpanels\viewlets,
where are default viewlets.

  2. Add a new CMF action with the CMF Action mechanism. Remember, the action
catalog should be 'panel_viewlets'. See the Install.py for detail

 How to add new panel skin?

  You can define a new css wrapper to define a new panel skin:

  1. customise contentpanels_skin.css.dtml, write your new css wrapper there
    
  2. go to ZMI 'portal_contentpanels', in the properties view, add your new
wrapper there.
      
Credits
    
  * "ZopeChina.com":http://www.zopechina.com, a leading Zope Service provider
   in China. ZopeChina.com runs the biggest Chinese Zope community in China -
   "CZUG.org":http://czug.org (China Zope User Group). We are trying to make
   Zope/Plone works better for Chinese people.
      
  * ausum's "CMFPortlets":http://www.zope.org/Members/ausum/CMFPortlets , many
   idea comes from CMFPortlets. Thanks!

Bug report and feature request

  CMFContentPanels is in
"Collective":http://sourceforge.net/projects/collective now. you can report
bugs and request new feature there.
