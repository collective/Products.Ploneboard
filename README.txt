Description

  This product is an add-on to Raphael Ritz's CMFBibliographyAT.


What It Does

  * Installs the 'Bibliography List' content type.

  * Installs the 'Bibref Custom Style' content type.

  * Installs the 'Bibref Custom Style Set' content type.

  * Installs the 'Bibref Custom Style Folder' content type.

  * Installs the 'portal_bibliolist' tool.

  * Installs default Bibref Styles in the 'portal_bibliolist' tool:

    - Minimal: Default minimal bibliography style.

    - APA: American Psychological Association bibliography style.
    
    - MLA: Modern Language Association style.

    - Chicago and Harvard styles.


Requirements

  * Plone 2+ / Archetypes 1.2.5+
  
  * CMFBibliographyAT


Installation

  * Recommanded: Copy ATBiblioList into your Products directory and install it with the 'QuickInstaller' Tool.

  * Or: create an external method at the root of your cmf portal and run it by clicking its 'test' tab.

    - Id            : InstallATBiblioList

    - Title         : Install ATBiblioList (optional)

    - Module Name   : InstallATBiblioList.Install

    - Function Name : install


Licence

  see LICENCE.txt


Contact

  David Convent - david.convent(at)naturalsciences(dot)be

  Louis Wannijn - louis.wannijn(at)naturalsciences(dot)be


To Do

  * Batch view for references widget.

  * complete translation (i18n) support (Done).

  * Better Documentation must be written.

  * Unit testing !!

  * Security: some functions still have no security declaration, hunting is open.

  * More BibrefStyles to come: We'll have to write more specific styles in order to meet the needs of our scientific staff.


Very possible future:

  * As suggested by a few testers/users, a 'very nice to have' functionnality of a bibliolist is to let the list be dynamically updated, based on previous search criteria.
    I think the best way to implement such a functionnality would be to make the BiblioList behave like cmf topics do.

  * For now, the search mechanism queries the portal catalog based on the SearchableText attribute. It was asked (by sarah and others) to let the user perform a search based on other criteria (like metadata). I believe that this will naturally be possible if the product behaves like a topic. If not, the search widget will be modified to extend the search possibilities.
