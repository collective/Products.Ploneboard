##parameters=content
from Products.CMFMetadata.Exceptions import BindingError

if content is None:
    return None

ms = context.portal_metadata

try:
    binding = ms.getMetadata(content)
except BindingError, be:
    # No binding found..
    return None

renderEdit = binding.renderElementEdit
renderView = binding.renderElementView

aquired_items = binding.listAcquired()
def isAcquired(set_name, element_name):
    if (set_name, element_name) in aquired_items:
        return 1
    return 0

isViewable = binding.isViewable
isEditable = binding.isEditable
value = binding.get

pt_binding = {}
pt_binding['setNames'] = set_names = binding.getSetNames()

# Build a dict for use in the pagetemplate,
# format:
# {
#  'setNames': [name1, name2,..],
#   set1: {'elementNames': [name1, name2,...],
#           element1: {'view':...,
#                      'isAcquired':...},
#                      'isEditable':...,
#                      'render':...,
#                      'isRequired':...},
#                      'isAcquirable':...},
#                      'description':...},
#                      'title':...},
#           element2:...
#         },
#   set2:...
# }

for set_name in set_names:
    pt_binding[set_name] = set = {}
    # Filter for viewable items
    set['elementNames'] = element_names = binding.getElementNames(
        set_name, mode='view')
    
    set_def = binding.getSet(set_name)
    set['setTitle'] = set_def.getTitle()
    set['setDescription'] = set_def.getDescription()
    
    # Per element:
    for element_name in element_names:
        set[element_name] = element = {}
        # view, maybe acquired
        element['view'] = renderView(set_name, element_name)
        # isAquired
        if isAcquired(set_name, element_name):
            element['isAcquired'] = 1
        else:
            element['isAcquired'] = 0        
        # isEditable, render
        if isEditable(set_name, element_name):
            element['isEditable'] = isEditable(set_name, element_name)
            element['render'] = renderEdit(set_name, element_name)
        else:
            # show a field, when it is read-only *and not* acquired (since
            # it then is show in the acquired content column anyway).
            if not element['isAcquired']:
                element['render'] = element['view']
            else:
                element['render'] = None
        # isRequired, isAcquirable, description, title
        bound_element = binding.getElement(set_name, element_name)
        element['isAcquireable'] = bound_element.isAcquireable()        
        element['isRequired'] = bound_element.isRequired()
        element['description'] = bound_element.Description()
        element['title'] = bound_element.Title()

return pt_binding
