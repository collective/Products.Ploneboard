##parameters=compopage_path, viewletId

request = context.REQUEST

viewlets = context.composite_tool.viewlets
viewlet = getattr(viewlets, viewletId)
context.setViewlet(viewlet.UID())

portal = context.portal_url.getPortalObject()
compo = portal.restrictedTraverse(compopage_path)
compo.incrementVersion('Change viewlet')

pageDesignUrl = compo.absolute_url() + '/design_view'
request.RESPONSE.redirect(pageDesignUrl)

