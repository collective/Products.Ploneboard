#-----------------------------------------------------------------------------
# Name:        UserTrackTool.py
# Purpose:     
#
# Author:      Philipp Auersperg
#
# Created:     2003/10/01
# RCS-ID:      $Id: UserTrackTool.py,v 1.1 2003/04/03 01:09:36 zworkb Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import Globals
from Globals import HTMLFile, InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore import CMFCorePermissions

try:
    from Products.UserTrack.UserTrack import UserTrack
    
except ImportError:
    print """\n\n\n***CMFUserTrackTool depends on the Zope product 'UserTrack' that can
be found on the same source as this product. Please install it and restart Zope***\n\n\n"""
    raise

class UserTrackTool( UserTrack, UniqueObject ):

    meta_type = 'CMF UserTrack Tool'
    id = 'portal_activeusers'
    
    def __init__(self):
        UserTrack.__init__(self)
        
    manage_options=UserTrack.manage_options
        

    security = ClassSecurityInfo()

InitializeClass( UserTrackTool )
