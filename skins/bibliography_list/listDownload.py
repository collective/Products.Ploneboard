## Script (Python) "listDownload"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format='BiBTex'
##title=
##
request = container.REQUEST
RESPONSE =  request.RESPONSE

if not format: return None

RESPONSE.setHeader('Content-Type', 'application/octet-stream')
RESPONSE.setHeader('Content-Disposition',
                   'attachment; filename=%s' %\
                   context.getId() + '.' + format)

bibtool = context.portal_bibliography
output = ''
field = context.getField('references_list')
for uid in getattr(context, field.edit_accessor)():
    obj = context.archetype_tool.lookupObject(uid = uid)
    output += bibtool.render(obj, format)

return output
    
