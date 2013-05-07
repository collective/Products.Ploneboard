## Controller Validator "validate_add_comment"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a posting

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.Ploneboard.utils import PloneboardMessageFactory as _

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

text = context.REQUEST.get('text', '');

if len(text) <= 0:
    state.setError("text", _(u"No content entered"), new_status="failure")

files=context.REQUEST.get('files', [])
maxsize=context.getConversation().getMaxAttachmentSize()

if maxsize!=-1:
    for file in files:
        if FileSize(file)>maxsize:
            state.setError("files", _(u"Attachment is too large"), new_status="failure")
            break

#Captcha validation
captcha_view = context.restrictedTraverse('@@captcha', None)
captcha_control = context.REQUEST.get('captcha_control', '')
if captcha_view and captcha_control:
    captcha = context.REQUEST.get('recaptcha_response_field', '')
    if not captcha_view.verify(captcha):
        state.setError('captcha', _('Wrong captcha. Try again'))
        state.set(status='failure')

if state.getErrors():
    _ = PloneMessageFactory
    message = _(u'Please correct the indicated errors.')
    putils.addPortalMessage(message)

return state
