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
# The title has to be set before the validation. This is the only place to do it
# right although it's looking hackish.
pfield = context.getPrimaryField()
if pfield:
    pfname = pfield.getName()
    title = form.get('title', context.Title())
    file = form.get('%s_file' % pfname, None)

    if not title and file:
        if file:
            filename = getattr(file, 'filename', None)

        if filename:
            form['title'] = filename
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
