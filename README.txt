CompositePack is a product that allows the Plone Manager to build composite
pages by manually aggregating archetype content from his site.

A composite page has a layout which defines its structure. 
Composition of content is made through the design view.
Composite elements are displayed through viewlets. 

Both layouts and viewlets are acquired from the skin, which implies they are
customizable.

Layouts and viewlets are registered through the composite_tool in ZMI (see
below how to register them).

Products required
=================
CompositePage 0.2
    http://hathawaymix.org/Software/CompositePage/CompositePage-0.2.tar.gz
kupu 
    HEAD of http://codespeak.net/svn/kupu/trunk/kupu
Archetypes
    release-1_3-branch from SF archetypes project - http://sf.net/projects/archetypes

Layouts
=======

The layout of a page is selected at creation time.
Layouts have slots which define the places where content can be added. Those
slots are named.

Layout can be changed later if needed. This is done through the edit view. When
changing the layout, if the old and new layouts share slot names, the content placed
in a slot of a given name in the old layout will be placed in the corresponding
slot in the new layout.  Content items placed in slots that do not have
corresponding names in the new layout are hidden, not deleted.  Switching back to
a layout will show items in their original location. Slots and composite
elements inaccessible through design view can be deleted through ZMI.

Design view
===========
The design view is supported in Mozilla and IE6.

The design view allows you to select the pieces of content : when clicking on one
of the dotted bars representing the slots, you get a menu.  There are two
options : 'Add..' and 'Add title...' (see below for more about titles).

To add a composite element, select 'Add...'  You get a popup window wherein you
can select the piece of content that you want to add to this slot.  This window
is a kupu drawer. It only shows instance of "composable" portal types (see
below for setting up composables).  You browse your site until you have found
the piece of content you want to display.  When you press ok, the composite
element is added to the composite page.  It is displayed through its default
viewlet.  Another viewlet can be selected later (see below).

Once added, the composite element can be moved by drag and drop from one slot
to another : drag and drop the icon associated with the composite element to
one of the dotted bars.

If you click the icon, you get another menu.  There are three options :
'Edit...', 'Delete' and 'Select viewlet'.

'Edit...' sends you to the edit screen of the content pointed at by the element.

'Delete' removes the composite element (not the associated content).

'Select viewlet' lists the available viewlets corresponding to the content type
of the composite element. Choose one of them to get your content displayed
differently.

Viewlets
========

Viewlets call templates(python scripts) that produce html excerpts.

CompositePack does what is needed to get a normal development situation :
the here (or context) variables are bound correctly.

Viewlets are mapped to content types : this allows to define different viewlets
for different types (see below how to register viewlets). For instance, image
content types have very specific needs. 


Titles
======
Titles are special composite elements which allows you to add some text when
composing your page.

In the design view, select 'Add title...'
You get a popup window with a prompt for the given title.
This adds a new composite element displaying the title through its registered
viewlet.

If you need to modify the title, access its data through the 'Edit...' item of
the icon menu.

Setting up composables
======================

- Go to the "kupu_library_tool" in Plone root (i.e. in \manage),

- Go to the "resources" tab,

- Add content types to the composable resource list (use the names displayed in
  the portal_types tool),

- Click Save button,

- Refresh your browser cache before to get the new javascript needed by the
  kupu drawers.

Registering a viewlet
=====================

- Create a page template (or python script) that returns an html excerpt,

- Go to the "composite_tool" in Plone root (i.e. in \manage),

- Inside the composite tool, go to the "viewlets" folder and add a
  CompositePack Viewlet using the button at the top.

    The CompositePack Viewlet has three fields :

    * "Short Name" - (Id) as usual,
    * "Title" which is the string that will be displayed in the navigation
       menu,
    * "Skin Method" - the name of the Page Template file created earlier.
            
    Now the viewlet is registered, next it needs to be mapped to the
    content types it should be used for.

- Go back to composite_tool folder. Go into "viewlets" tab where
the registered viewlets can be mapped to the content types.

    If the viewlet is to be used with all content types, add it to the
    "Default Setup" by selecting it in the "Viewlets" list box (use the
    Ctrl button to select multiples, otherwise you will deselect those
    already mapped).

    If the viewlet is to be used for specific types only, select it in
    the "Viewlets" list box of the corresponding types.

    The "Default Viewlet" dropdown box on the right hand side allows
    you to setup the viewlet that will be used by default for each of
    the corresponding types.

- Press the Change button at the bottom of this form to apply the
changes. The viewlet can now be used.

Registering a layout
====================

- Create a page template which uses TALES slot expression (look at one of the
  existing layouts to understand it). The template should be based on plone
  main_template.

- Go to the "composite_tool" in Plone root (i.e. in \manage),

- Inside the composite tool, go into the "layouts" folder and add a
CompositePack Viewlet using the button at the top.

    The CompositePack Viewlet has three fields :

    * "Short Name" (Id) as usual,
    * "Title" which is the string that will be displayed in the dropdown widget
      for layout selection,
    * "Skin Method" - the name of the Page Template file created earlier.
            
    The layout is registered.
