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
$Id: utils.py,v 1.1 2004/05/01 16:55:10 tiran Exp $
""" 

__author__  = 'Christian Heimes'
__docformat__ = 'restructuredtext'

from Products.CMFCore.utils import getToolByName

def setupMimeTypes(self, typeInfo, old=(), moveDown=(), out=None):
    reg = getToolByName(self, 'content_type_registry')
    
    moveBottom = []
    moveTop = []

    for o in old:
        # remove old
        if reg.getPredicate(o):
            reg.removePredicate(o)
    
    for t in typeInfo:
        klass       = t['klass']
        portal_type = t['portal_type']

        if not IATContentType.isImplementedByInstancesOf(klass):
            # not a AT ContentType (maybe criterion) - skip
            continue
        
        # major minor
        for name, mm in getMajorMinorOf(klass):
            if reg.getPredicate(name):
                reg.removePredicate(name)
            reg.addPredicate(name, 'major_minor')
            reg.getPredicate(name).edit(**mm)
            reg.assignTypeName(name, portal_type)
            for iface in moveDown:
                if iface.isImplementedByInstancesOf(klass):
                    moveBottom.append(name)
        # extensions
        name, extlist = getFileExtOf(klass)
        if extlist:
            if reg.getPredicate(name):
                reg.removePredicate(name)
            reg.addPredicate(name, 'extension')
            reg.getPredicate(name).edit(extlist)
            reg.assignTypeName(name, portal_type)
            for iface in moveDown:
                if iface.isImplementedByInstancesOf(klass):
                    moveBottom.append(name)
            else:
                moveTop.append(name)

    # move ATFile to the bottom because ATFile is a fallback
    last = len(reg.listPredicates())-1
    for name in moveBottom:
        reg.reorderPredicate(name, last)
        
    # move extension based rules to the top
    for name in moveTop:
        reg.reorderPredicate(name, 0)

def getMajorMinorOf(klass):
    """helper method for setupMimeTypes
    """
    retval = []
    for mt in klass.assocMimetypes:
        ma, mi = mt.split('/')
        if mi == '*':
            mi   = ''
            name = '%s' % ma
        else:
            name = '%s_%s' % (ma, mi)
        retval.append( (name, {'major' : ma, 'minor' : mi}) )
    return retval

def getFileExtOf(klass):
    """helper method for setupMimeTypes
    """
    name = '%s_ext' % klass.meta_type
    return (name, klass.assocFileExt)

def registerTemplates(self, typeInfo, out):
    """
    """
    atTool = getToolByName(self, 'archetype_tool')
    for t in typeInfo:
        klass          = t['klass']
        meta_type      = klass.meta_type
        default_view = getattr(klass, 'default_view', 'base_view')
        suppl_views    = getattr(klass, 'suppl_views', ())

        views = ['base_view',]

        if default_view != 'base_view':
            atTool.registerTemplate(default_view)
            views.append(default_view)

        for view in suppl_views:
            atTool.registerTemplate(view)
            views.append(view)

        atTool.bindTemplate(meta_type, views)
