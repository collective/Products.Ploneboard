##parameters=compopage_path, target_path

portal = context.portal_url.getPortalObject()

destination = portal.restrictedTraverse(target_path)
factory = destination.manage_addProduct['CompositePack'].manage_addElement

new_id = context.generateUniqueId()
new_id = factory(id=new_id)
new_ob = getattr(destination, new_id)

uid = context.UID()
new_ob.setTarget(uid)

compo = portal.restrictedTraverse(compopage_path)
compo.incrementVersion('Add element')
pageDesignUrl = compo.absolute_url() + '/design_view'

return context.REQUEST.RESPONSE.redirect(pageDesignUrl)
