request = context.REQUEST
ms = context.portal_metadata
binding = ms.getMetadata(context)

all_errors = {}
for set_name in binding.getSetNames():
    errors = binding.setValuesFromRequest(set_name, request, reindex=1)
    if errors:
        all_errors[set_name] = errors

if all_errors:
    msg = 'Metadata input had validation errors.'
else:
    msg = 'Metadata saved.'

request.set('portal_status_message',msg)

#return str(all_errors)

return context.metadata_view(
    form_errors=all_errors,
    )
