##parameters=viewletId

ct = context.composite_tool
viewlet = getattr(ct, viewletId)

#context.getField('viewlet').set(context, viewlet.UID())
context.setViewlet(viewlet.UID())
request = context.REQUEST
pageDesignUrl = request.URL4 + "/design?ui=plone"
request.RESPONSE.redirect(pageDesignUrl)

