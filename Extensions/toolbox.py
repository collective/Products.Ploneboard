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
$Id: toolbox.py,v 1.4 2004/05/04 18:26:23 tiran Exp $
""" 

__author__  = 'Jens Klein, Christian Heimes'
__docformat__ = 'restructuredtext'

from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.types import ATDocument, ATEvent, ATFavorite, \
    ATFile, ATFolder, ATImage, ATLink, ATNewsItem, ATTopic
from Products.ATContentTypes.interfaces.IATImage import IATImage
from Products.ATContentTypes.interfaces.IATDocument import IATDocument
from Acquisition import aq_base


not_global_allow = ('Favorite', 'Large Plone Folder')

atct_klasses = (
    ATDocument.ATDocument,
    ATEvent.ATEvent,
    ATFavorite.ATFavorite,
    ATFile.ATFile,
    ATFolder.ATFolder,
    ATFolder.ATBTreeFolder,
    ATImage.ATImage,
    ATLink.ATLink,
    ATNewsItem.ATNewsItem,
    ATTopic.ATTopic,
   )

def recreateATImageScales(self):
    """Recreates AT Image scales (doesn't remove unused!)
    """
    out = StringIO()
    print >>out, "Updating AT Image scales"
    catalog = getToolByName(self, 'portal_catalog')
    brains  = catalog(portal_type = ('ATImage', 'Image'))
    for brain in brains:
        obj = brain.getObject()
        if not obj:
            continue
        if not IATImage.isImplementedBy(obj):
            continue
        field = obj.getField('image')
        if field:
            print >>out, 'Updating %s' % obj.absolute_url(1)
            field.createScales(obj)

    return out.getvalue()

def _switchToATCT(pt, cat, reg, klass, out):
    """
    """
    atId = klass.__name__
    id = klass.newTypeFor[0]
    bakId = 'CMF %s' % id

    title = klass.archetype_name[3:]
    bakTitle = bakId
    
    # move away the disabled type
    pt.manage_renameObject(id, bakId)
    pt[bakId].manage_changeProperties(title=bakTitle, global_allow=0)
    _changePortalType(cat, id, bakId)
    print >>out, '%s -> %s (%s)' % (id, bakId, bakTitle)

    # rename to the new
    pt.manage_renameObject(atId, id)
    pt[id].manage_changeProperties(title=title)
    _changePortalType(cat, atId, id)
    print >>out, '%s -> %s (%s)' % (atId, id, title)

    # adjust the content type registry
    preds = reg.listPredicates()
    for predid, pred in preds:
        typ = pred[1]
        if typ == atId:
            reg.assignTypeName(predid, id) 

def _switchToCMF(pt, cat, reg, klass, out):
    """
    """
    atId = klass.__name__
    id = klass.newTypeFor[0]
    bakId = 'CMF %s' % id

    atTitle = klass.archetype_name
    
    # move away the ATCT type
    pt.manage_renameObject(id, atId)
    pt[atId].manage_changeProperties(title=atTitle)
    _changePortalType(cat, id, atId)
    print >>out, '%s -> %s (%s)' % (id, atId, atTitle)

    # rename to the new type
    pt.manage_renameObject(bakId, id)
    if id not in not_global_allow:
        global_allow = 1
    else:
        global_allow = 0
    pt[id].manage_changeProperties(title='', global_allow=global_allow)
    _changePortalType(cat, bakId, id)
    print >>out, '%s -> %s (%s): %i' % (bakId, id, '', global_allow)

    # adjust the content type registry
    preds = reg.listPredicates()
    for predid, pred in preds:
        typ = pred[1]
        if typ == id:
            reg.assignTypeName(predid, bakId)

def _changePortalType(cat, old, new):
    """
    """
    brains = cat(portal_type = old)
    objs = [brain.getObject() for brain in brains ]
    for obj in objs:
        if not obj:
            continue
        obj._setPortalTypeName(new)

def switchCMF2ATCT(self):
    if isSwitchedToATCT(self):
        return "Error: Already switched"
    pt = getToolByName(self,'portal_types')
    cat = getToolByName(self,'portal_catalog')
    reg = getToolByName(self, 'content_type_registry')
    out = StringIO()
    for klass in atct_klasses:
        _switchToATCT(pt, cat, reg, klass, out)
    return out.getvalue()

def switchATCT2CMF(self):
    if not isSwitchedToATCT(self):
        return "Error: Not switched"
    pt = getToolByName(self,'portal_types')
    cat = getToolByName(self,'portal_catalog')
    reg = getToolByName(self, 'content_type_registry') 
    out = StringIO()
    for klass in atct_klasses:
        _switchToCMF(pt, cat, reg, klass, out)
    return out.getvalue()

def isSwitchedToATCT(self):
    pt = getToolByName(self,'portal_types')
    doc = pt.getTypeInfo('Document')
    if doc and doc.meta_type == ATDocument.ATDocument.meta_type:
        return 1
    else:
        return 0