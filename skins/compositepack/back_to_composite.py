request = context.REQUEST
compo = context.dereferenceComposite()
compo.incrementVersion('Edit title')
url = compo.absolute_url() + "/design_view"
msg = request.get('portal_status_message', None)
if not msg is None:
    url += '?portal_status_message=' + msg
request.RESPONSE.redirect(url)
