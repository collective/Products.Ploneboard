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
from Products.Ploneboard.utils import PloneboardMessageFactory as _

putils = getToolByName(context, 'plone_utils')

#Hardening enable mimetypes validation with a list of allowed types
hardening_tool = getToolByName(context, 'rer_hardening_tool', None)

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

if len(title) <= 0:
    state.setError("title", _(u"No title entered"), new_status="failure")

files=context.REQUEST.get('files', [])
maxsize=context.getMaxAttachmentSize()

if maxsize!=-1 or hardening_tool:
    for file in files:
        filesize = FileSize(file)
        if filesize:
            if filesize>maxsize:
                state.setError("files", "Attachment is too large", new_status="failure")
                break
            if hardening_tool:
                validation_report = hardening_tool.validateInputFile(file)
                if not validation_report.get('is_valid', False):
                    state.setError("files", validation_report.get('message', "Attachment type not allowed"), new_status="failure")
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
        message = _(u'Please correct the indicated errors.')
        putils.addPortalMessage(message)

return state
