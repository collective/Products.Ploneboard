## Controlled Python Script "search_amazon_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=author='', title='', keywords='', subject='', isbn='', publisher=''
##title=Make sure that at least one field has been filled out
##

if not author and not title and not keywords and not subject and not isbn and not publisher:
    state.setStatus('failure')
    return state.set(status='failure', portal_status_message='Enter an author, title, keywords, subject, ISBN, or a publisher to search')
return state