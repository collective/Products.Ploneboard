## Script (Python) "contentpanels_error"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# raise # uncomment this line for viewlet debug

error=_['error']
if error.type == 'Unauthorized':
  return ""
else:
  err_log = context.error_log

  return """<p>An error ocurred.</p>
            <p>Error type: %s</p>
            <p>Error value: %s</p>""" % (error.type, error.value)

