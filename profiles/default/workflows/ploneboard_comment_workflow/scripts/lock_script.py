## Script (Python) "lock_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sci
##title=
##
# Dispatch to more easily customizable methods
object = sci.object
# We don't have notifyPublished method anymore
#object.notifyPublished()

wftool = sci.getPortal().portal_workflow

# Try to make sure that conversation and contained messages are in sync
if object.portal_type == 'Message':
    parent = object.aq_inner.aq_parent
    if parent.portal_type == 'Conversation':
        try:
            if wftool.getInfoFor(parent,'review_state',None) == sci.old_state.getId():
                wftool.doActionFor(parent, sci.transition.getId())
        except:
            pass

# Lock all messages when locking conversation
if object.portal_type == 'Conversation':
    for message in object.contentValues('Message'):
        try:
            if wftool.getInfoFor(message,'review_state',None) == sci.old_state.getId():
                wftool.doActionFor(message, sci.transition.getId())
        except:
            pass
