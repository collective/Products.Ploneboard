## Script (Python) "contentpanels_getPanel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objectPath, panelSkin
##title=

try:
    if objectPath == 'None':
        panelObject = context
    elif objectPath[0] != '/':
        panelObject = getattr(context.aq_parent, objectPath)
    else :
        panelObject = context.restrictedTraverse(objectPath)

    return panelObject.object_skin_panel(panelObject, panelSkin=panelSkin)

except Exception,e:
    print 'Sorry, Object in this panel was Deleted!<br/>'
    print 'Please delete this panel. '
    #from zLOG import LOG, INFO
    #LOG(script.id,INFO,str(e))
    #raise
    return printed

