from Products.CMFCore.utils import getToolByName
#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA 
#
"""

$Id: Install.py,v 1.1 2004/03/08 10:48:40 tiran Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from Products.Archetypes import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from StringIO import StringIO
from Products.ATContentTypes.config import *

def install(self):
    out = StringIO()

    classes = listTypes(PROJECTNAME)
    installTypes(self, out,
                 classes,
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)

    #register folderish classes in use_folder_contents
    props=getToolByName(self,'portal_properties').site_properties
    use_folder_tabs=list(props.use_folder_tabs)

    print >> out, 'adding classes to use_folder_tabs:'
    for cl in classes:
        print >> out,  'type:',cl['klass'].portal_type
        if cl['klass'].isPrincipiaFolderish:
            use_folder_tabs.append(cl['klass'].portal_type)
    
    print >> out, 'Successfully installed %s' % PROJECTNAME
    return out.getvalue()

def uninstall(self):
    out = StringIO()
    classes=listTypes(PROJECTNAME)

    #unregister folderish classes in use_folder_contents
    props = getToolByName(self,'portal_properties').site_properties
    use_folder_tabs = list(props.use_folder_tabs)

    print >> out, 'removing classes from use_folder_tabs:'
    for cl in classes:
        print >> out,  'type:', cl['klass'].portal_type
        if cl['klass'].isPrincipiaFolderish:
            if cl['klass'].portal_type in use_folder_tabs:
                use_folder_tabs.remove(cl['klass'].portal_type)

    props.use_folder_tabs=tuple(use_folder_tabs)

    return out.getvalue()
