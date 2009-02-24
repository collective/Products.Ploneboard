## Controller Validator "validate_add_conversation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a posting
# $Id$
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

reg_tool=context.portal_registration 
putils = getToolByName(context, 'plone_utils')

def FileSize(file):
    if hasattr(file, 'size'):
        size=file.size
    elif hasattr(file, 'tell'):
        file.seek(0, 2)
        size=file.tell()
        file.seek(0)
    else:
        try:
            size=len(file)
        except TypeError:
            size=0

    return size/1024

title = context.REQUEST.get('title', '');
name = context.REQUEST.get('name', '')
email = context.REQUEST.get('email', '')

if len(name) <= 0:
    state.setError("name", _(u"No name entered"), new_status="failure")
if not email:
    state.setError('email', _(u'Please submit an email address.'), 'sender_from_address_required')
else:
    if reg_tool.isValidEmail(email):
        pass
    else:
        state.setError('email', _(u'You entered an invalid email address.'), 'invalid_email')


if len(title) <= 0:
    state.setError("title", "No title entered", new_status="failure")

files=context.REQUEST.get('files', [])
maxsize=context.getMaxAttachmentSize()

if maxsize!=-1:
    for file in files:
        if FileSize(file)>maxsize:
            state.setError("files", "Attachment is too large", new_status="failure")
            break

if state.getErrors():
    message = _(u'Please correct the indicated errors.')
    putils.addPortalMessage(message)

return state
