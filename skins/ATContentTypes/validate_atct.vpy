## Script (Python) "validate_atct"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##
errors  = {}
request = context.REQUEST
form    = request.form

## XXX It's hacky and not nice but it's working
# Set the title from the filename of uploaded image or field
title = form.get('title', context.Title())
image = form.get('image_file', None)
file  = form.get('file_file', None)

if not title and (image or file):
    if image:
        filename = getattr(image, 'filename', None)
    if file:
        filename = getattr(file, 'filename', None)

    if filename:
        request.form['title'] = filename
## eoXXX

errors  = context.validate(REQUEST=request, errors=errors, data=1, metadata=0)

if errors:
    return state.set(status='failure', errors=errors, portal_status_message='Please correct the indicated errors.')

message = 'Your changes have been saved.'
tidiedFields = request.get('tidiedFields', None)
if tidiedFields:
    message = '%s mxTidy has fixed the HTML code of the following field(s): %s' % \
              (message, ', '.join([field.widget.Label(context) for field in tidiedFields]))

return state.set(portal_status_message=message)
