## Script (Python) "publish_script"
##parameters=sci

object = sci.object

wftool = sci.getPortal().portal_workflow

# Try to make sure that conversation and contained messages are in sync
if object.portal_type == 'PloneboardComment':
    parent = object.aq_inner.aq_parent
    if parent.portal_type == 'PloneboardConversation':
        try:
            if parent.getNumberOfMessages() == 0 and wftool.getInfoFor(parent,'review_state',None) == sci.old_state.getId():
                wftool.doActionFor(parent, sci.transition.getId())
        except:
            pass

# Reject all (really just one if their current workflow are the same) messages when rejecting conversation
if object.portal_type == 'PloneboardConversation':
    for message in object.contentValues('PloneboardComment'):
        try:
            if wftool.getInfoFor(message,'review_state',None) == sci.old_state.getId():
                wftool.doActionFor(message, sci.transition.getId())
        except:
            pass
