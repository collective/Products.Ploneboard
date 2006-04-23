## Script (Python) "autopublish_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sci
##title=
##
object = sci.object

wftool = sci.getPortal().portal_workflow

# Try to make sure that conversation and contained messages are in sync
if object.portal_type == 'PloneboardComment':
    parent = object.aq_inner.aq_parent
    if parent.portal_type == 'PloneboardConversation':
        try:
            if wftool.getInfoFor(parent,'review_state',None) in (sci.old_state.getId(), 'pending'):
                wftool.doActionFor(parent, 'make_active')
        except:
            pass
