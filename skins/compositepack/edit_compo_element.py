content = context.dereference()
context.REQUEST.RESPONSE.redirect(content.absolute_url()+ '/base_edit')
