##parameters=compopage_path, target_path


#print compopage_path
#print target_path
#return printed

portal = context.portal_url.getPortalObject()
uid = context.UID()

compo = portal.restrictedTraverse(compopage_path)
return_to = compo.absolute_url() + '/design?ui=plone'

destination = portal.restrictedTraverse(target_path)
new_id = context.generateUniqueId()

factory = destination.manage_addProduct['CompositePack'].manage_addElement
new_id = factory(id=new_id)
new_ob = getattr(destination, new_id)
new_ob.setTarget(uid)

return context.REQUEST.RESPONSE.redirect(return_to)
