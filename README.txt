What is CMFContentPanels?

  Have you tried the famous "CMFportalts":http://www.zope.org/Members/ausum/CMFPortlets ? Do you want another one which store portlets layout information in a CMF content to build public portlets page but not in a member's private memberdata? Do you want to support more existing contents without creating any new content type? Do you want a easier way to write new box skins? Do you want a total Plone support and more clean code?

  Maybe CMFContentPanels is an alternative now. CMFContentPanels is totally rewrite from CMFPortlets. It is a CMF/Plone Content which have panels showing other contents to build complex page easily. You can change the box skin for each content panel.

Features

  * All the things CMFPortlet0.5 have!!

  * CMFContentPanels is a cmf content. You can build mulity public complex page for anonymous users. 

  * Extensible to support more contents. It supports Documents, Topic, CMFForum, NeoBoard, Folder, CMFWikiPage by defaults. You can write new panel views for other contents and register them to CMFContentPanels.

  * Copy and select operation is more natural way to add new content panels.

  * Plone compatible. And we just test it with Plone only.

  * Extensible to support more panel box skins. you can write a new skin with PageTemplate Slots and register it to CMFContentPanels. It is easy enough!

How to Use it?

  1. Install it. See INSTALL.txt for more information.

  2. Add a new ContentPanels: like other content, select CMFContentPanels from the add list in plone, and Add it.

  3. Add content to Contentpanels as a panel: 

    * In the plone folder, select the conent you want to add, click 'Copy' button.

    * go back to the new added ContentPanels, click the CMF Tool icon  on the top right of the page to edit the ContentPanels(we should use another better icon later).

    * now it is a familiar page for CMFPortlets Users. You can find the copied content from content add list. And you can choose a skin for it. Click add and you get it!

  4. And you can add/delete page, add/delete columns, add/delete panels, Change Column width just like CMFPortlets. This way you can get what you want.

How to support other content?

  1. write a panel view page for your content. You can refer to stuff at \CMFContentPanels\skins\contentpanels\content_views

  2. customize "contentpanels_panelviewer_registry" to add your content support.

How to add new panel box skin?

  1. write your panel box skin. you can refer to stuff at \CMFContentPanels\skins\contentpanels\panel_slots

  2. customize "contentpanels_slots_registry" to add you box skin.

todo list

  * use portal_properties to store content registry and box skin registry.

  * i found the 'copy' operation in Zope needs a very high permission. We should find a better way to select a content.

  * Rows support in ContentPanels.

  * Move panels.

  * Use DHTML to build a more easy use layout adjust interface.

Credits

  * "ZopeChina.com":http://zopechina.ods.org, a leading Zope Service provider in China. ZopeChina.com runs the biggest Chinese Zope community in China - "CZUG.org":http://czug.ods.org (China Zope User Group). We are trying to make Zope/Plone works better for Chinese people. 

  * ausum's "CMFPortlets":http://www.zope.org/Members/ausum/CMFPortlets , many idea comes from CMFPortlets. Thanks!
