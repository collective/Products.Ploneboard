##parameters=viewletId
viewlets = context.composite_tool.viewlets
viewlet = getattr(viewlets, viewletId)
context.setViewlet(viewlet.UID())

request = context.REQUEST
pageDesignUrl = request.URL4 + "/design?ui=plone"
request.RESPONSE.redirect(pageDesignUrl)

