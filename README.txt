README for PloneBannerManager, 
a banner management product for Plone 2 and Archetypes
(c) 2004 Osma Suominen <osma.suominen@mbconcert.fi>

Tested with:

  * Zope 2.6.2 (Python 2.1.3 on FreeBSD)

  * Plone 2.0RC3

  * Archetypes 1.2.3

May work with other versions as well.

Features

  * supports common image types

  * counts views and clicks

  * optionally open link in new window

  * able to set limits on no. of views and no. of clicks

  * ability to set banner weights to favor some banners over others

  * comes with a very simple workflow (2 states, private/published) and adds
    a new Permission, so you can give the permissions to manage banners to a
    user account or group without giving them other permissions

  * supports i18n; currently only Finnish translation available

Installation

  For installation instructions, see INSTALL.txt

  (short story: just use portal_quickinstaller)

Usage

  To use this Product, you first have to create one or more Banner Folders
  to store your banners. The Banner Folders are independent so you can have
  one set of banners for one kind of use (e.g. to show in the top part of the
  page template) and another set for another use (e.g. portlets showing
  banners).

Banners in Page Templates

  To add a banner to your main_template, you must customize it and add the
  following code somewhere. Of course you can add this to any template.
  The '<div>' is optional but good for styling with CSS etc.

  Example::

    <div id="portal-banner">
    <span tal:define="banner here/banners/getBanner"
          tal:condition="nocall:banner"
          tal:replace="structure banner/tag"/>
    </div>

  where 'banners' is the name of the Banner Folder.

Banner Portlet

  This product also includes a banner portlet. It is not a macro but a
  callable page template, because in that way you can use context to determine
  the Banner Folder from which to choose the banner.

  To use it, add this to your left_slots or right_slots::

    here/banners/portlet_banner

  where 'banners' is the name of the Banner Folder.

Credits

  This Product incorporates some code derived from Plone and other sources.
  Please see CREDITS.txt for more information.


This product is licensed under GPL:

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, 
  MA 02111-1307 USA
