request = context.REQUEST
url = request.URL3 + "/design_view"
msg = request.get('portal_status_message', None)
if not msg is None:
    url += '&portal_status_message=' + msg
request.RESPONSE.redirect(url)
