from Products.CMFUserTrackTool.UserTrackTool import UserTrackTool
from Products.CMFCore.utils import getToolByName, manage_addTool
import string
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFUserTrackTool import usertrack_globals

def install( self ):
    slotpath='here/activeusers_slot/macros/activeusersBox'
    #create the tool instance
    portal = getToolByName(self,'portal_url').getPortalObject()
    #addPloneTool=portal.manage_addProduct['CMFPlone'].manage_addTool
    #print 'Test',portal.__class__
    #addPloneTool('CMF UserTrack Tool',None)

    tracker = UserTrackTool()
    portal._setObject(tracker.getId(),tracker)
    
    try: #try to install the slot (bare except, because it will fail on bare CMF)
        if not slotpath in portal.right_slots:
            portal.right_slots = list(portal.right_slots) + [slotpath,]
    except: 
        pass
        
    # setup skins
    skinstool = getToolByName(self,'portal_skins')
    if 'usertrack' not in skinstool.objectIds():
        addDirectoryViews( skinstool, 'skins', usertrack_globals )

    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath( skin )
        path = map( string.strip, string.split(path, ',') )
        if 'usertrack' not in path:
            try: path.insert( path.index('content'), 'usertrack' )
            except ValueError:
                path.append( 'usertrack' )

            path = string.join( path, ', ' )
            skinstool.addSkinSelection( skin, path )

    return 'OK'

