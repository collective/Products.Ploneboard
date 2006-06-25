## Script (Python) "moderation.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Searches for pending comments in moderated boards
##
# Search the catalog, and depending on where the script is called from, filter
# and massage results until it is suitable for displaying. The main concern is
# too large number of search results.
# Massaging the results means getting the objects, which might not be that bad
# as we are going to write to them anyway (moderate) soon.
# Returned results might be forum objects, conversation objects or comment objects
# if returned number of pending comments is less than 100: display everything
# if context is conversation, display everything
# if context is board, only display link to forums with more than 50 pending comments
# if context is forum, only display link to conversations with more than 10 pending comments
 
query = {}
query['sort_on'] = 'created'
query['review_state'] = 'pending'
query['portal_type'] = 'PloneboardComment'
query['path'] = '/'.join(context.getPhysicalPath())

reqget = context.REQUEST.get

def supplement_query(field, index_name=None, reqget=reqget, query=query):
    if not index_name: index_name = field
    val = reqget(field, None)
    if val:
        query[index_name] = val

catalogresult = context.portal_catalog(query)

if context.portal_type == 'PloneboardConversation' or len(catalogresult) < 100:
    return [r.getObject() for r in catalogresult]

result = []
if context.portal_type == 'Ploneboard':
    for forum in context.contentValues('PloneboardForum'):
        query['path'] = '/'+ '/'.join(forum.getPhysicalPath()[1:])
        forumresult = context.portal_catalog(query)
        if len(forumresult) > 50:
            result.append(forum)
        else:
            result.extend([r.getObject() for r in forumresult])
    return result

if context.portal_type == 'PloneboardForum':
    # We need a dynamic programming solution here as search for each 
    # conversation is prohibitively expensive
    forumid = context.getId()
    conversations = {} # {id, [commentbrains, ]}
    for item in catalogresult:
        pathlist = item.getPath().split('/')
        conversationid = pathlist[pathlist.index(forumid)+1]
        if conversations.has_key(conversationid):
            conversations[conversationid].append(item)
        else:
            conversations[conversationid] = [item]
    for key in conversations.keys():
        if len(conversations[key]) > 10:
            # Could use a wrapper to store the conversation + length of pending comment
            # queue to avoid catalog calls in the moderation_form template
            result.append(context.getConversation(key))
        else:
            result.extend([i.getObject() for i in conversations[key]])

return result