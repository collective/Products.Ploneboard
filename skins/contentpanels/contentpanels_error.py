## Script (Python) "contentpanels_error"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

error=_['error']
if error.type == 'Unauthorized':
  return ""
else:
  err_log = context.error_log
  # err_log.raising(sys.exc_info())

  return """<p>An error ocurred.</p>
            <p>Error type: %s</p>
            <p>Error value: %s</p>""" % (error.type, error.value)

