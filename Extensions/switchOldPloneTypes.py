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
$Id: switchOldPloneTypes.py,v 1.1 2004/03/13 23:25:32 yenzenz Exp $
""" 

__author__  = 'Jens Klein'

def switch_old_plone_types_off(self):
    ''' switch OldPloneTypes Off by setting its global_allow property in 
        portal_types tool to 0
    '''
    switch_old_plone_types(self,0)

def switch_old_plone_types_on(self):
    ''' switch OldPloneTypes Off by setting its global_allow property in 
        portal_types tool to 0
    '''
    switch_old_plone_types(self,1)
    
def switch_old_plone_types(self, state):
    ''' toggle OldPloneTypes On/Off by setting its global_allow property in 
        portal_types tool
    '''
    
    assert state in [1,0]
    
    from Products.CMFCore.utils import getToolByName
    pt   = getToolByName(self,'portal_types')
    
    typesmap=[ \
        # schema of this map:
            # (old plone type id, old plone type title)
            # (new plone type id, new plone type title)
            # 1 or 0 -> default of global allow
        (
            ('Large Plone Folder', 'Large Plone Folder'),    
            ('ATBTreeFolder',      'AT BTree Folder'),
            0,
        ),
        (
            ('Document','Document'),
            ('ATDocument','AT Document'),   
            1,
        ),
        (
            ('Event','Event'),
            ('ATEvent','AT Event'),
            1,
        ),
        (
            ('Favorite','Favorite'),
            ('ATFavorite','AT Favorite'),   
            1,
        ),
        (
            ('File','File'),
            ('ATFile','AT File'),   
            1,
        ),        
        (
            ('Folder','Folder'),
            ('ATFolder','AT Folder'),
            1,
        ),
        (
            ('Image','Image'),
            ('ATImage','AT Image'),
            1,
        ),
        (
            ('Link','Link'),
            ('ATLink','AT Link'),
            1,
        ),
        (
            ('News Item','News Item'),
            ('ATNewsItem','AT News Item'),  
            1,
        ),
        (
            ('Topic','Topic'),
            ('ATTopic','AT Topic'),
            1,
        ),
        # do not rename the criterias for ATTopic.
    ]
    
    for typetuple in typesmap:        
        if not state:
            # disable global allow
            pt[typetuple[0][0]].manage_changeProperties(global_allow=0)
            # prefix old types title with 'CMF '
            pt[typetuple[0][0]].manage_changeProperties(title='CMF '+typetuple[0][1])
            # change title of the AT Type to old types title
            pt[typetuple[1][0]].manage_changeProperties(title=typetuple[0][1])
        else:
            # set  global allow to default
            pt[typetuple[0][0]].manage_changeProperties(global_allow=typetuple[2])
            # restore AT types title to default
            pt[typetuple[1][0]].manage_changeProperties(title='AT '+typetuple[0][1])
            # restore old types title to default
            pt[typetuple[0][1]].manage_changeProperties(title=typetuple[0][1])
        
        