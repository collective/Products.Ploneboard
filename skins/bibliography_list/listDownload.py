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

output = ''
bibtool = context.portal_bibliography
ref_types = bibtool.getReferenceTypes()

for entry in context.getReferences_list():
    obj = context.archetype_tool.lookupObject(uid = entry)
    output += bibtool.render(obj, format)

return output
    
