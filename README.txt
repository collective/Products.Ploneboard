Description

  This product is an add-on to Raphael Ritz's CMFBibliographyAT.
  It lets portal users organize existing bibliography references
  into lists.
  Bibliography lists can be displayed using one of the standard
  (file system based) bibliography styles shiped with the product,
  or using custom bibliography styles designed by protal users.

  It should not be too difficult for a python programmer to write its own
  file system based bibliography styles. If you do so, please share your
  interesting bibliography styles with the community.


What It Does

  * Installs the 'Bibliography List' content type.

  * Installs the 'Bibref Custom Style' content type.

  * Installs the 'Bibref Custom Style Set' content type.

  * Installs the 'Bibref Custom Style Folder' content type.

  * Installs the 'portal_bibliolist' tool.

  * Installs FS based Bibref Styles in the 'portal_bibliolist' tool:

    - Minimal: Default minimal bibliography style.

    - APA: American Psychological Association bibliography style.
    
    - MLA: Modern Language Association style.

    - Chicago and Harvard styles.


Requirements

  * Plone 2+ / Archetypes 1.2.5+
  
  * CMFBibliographyAT (cvs.sourceforge.net:/cvsroot/collective)

  * Epoz 0.8.x


Installation

  - First, add the product to Zope:

    * extract the product from its archive and move it to the Products directory of your Zope Instance.

  - Then, install the product in Plone:

    * Recommended (Plone way): use the 'QuickInstaller' Tool from the ZMI, or go to 'Plone Setup > Add/Remove Products' in the Plone User Interface. Check the corresponding checkbox and click the 'install' button.

    * Alternate (CMF Manual way): create an external method at the root of your cmf portal and run it by clicking its 'test' tab.

    External Method parameters:

    - Id: InstallATBiblioList

    - Title: Install ATBiblioList (optional)

    - Module Name: InstallATBiblioList.Install

    - Function Name: install


Documentation

  More documentation can be found in the 'doc' folder of this product.


Licence

  see LICENCE.txt


Contact

  David Convent - david.convent(at)naturalsciences(dot)be

  Louis Wannijn - louis.wannijn(at)naturalsciences(dot)be


Changes

  Version 0.3

  * Sort lists by 1st Author name and publication year.

  * complete translation (i18n) support.

  * Better Documentation.

To Do

  * Batch view for references widget.

  * Reference Browser support (ATReferenceBrowserWidget might be useful here)

  * Unit testing !!

  * Security: some functions still have no security declaration, hunting is open.

  * More BibrefStyles to come: We'll have to write more specific styles in order to meet the needs of our scientific staff.


Very possible future:

  * As suggested by a few testers/users, a 'very nice to have' functionnality of a bibliolist is to let the list be dynamically updated, based on previous search criteria.
    I think the best way to implement such a functionnality would be to make the BiblioList behave like cmf topics do.

  * For now, the search mechanism queries the portal catalog based on the SearchableText attribute. It was asked (by sarah and others) to let the user perform a search based on other criteria (like metadata). I believe that this will naturally be possible if the product behaves like a topic. If not, the search widget will be modified to extend the search possibilities.


