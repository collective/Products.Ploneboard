## Script (Python) "getKeyedForums"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=forums=None
##title=Get forums keyed on category
##

if forums is None:
    forums = context.getForums()

result = {}

for forum in forums:
    if hasattr(forum, 'getCategory'):
        categories = forum.getCategory()
        if not categories:
            categories = None
        if not same_type(categories, ()) and not same_type(categories, []):
            categories = categories,
        for category in categories:
            try:
                categoryforums = result.get(category, [])
                categoryforums.append(forum)
                result[category] = categoryforums
            except TypeError: # category is list?!
                result[', '.join(category)] = forum
return result