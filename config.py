""" File containing the displaylists for the different string formats (these lists are used in the selection boxes in formatting files)"""

from Products.Archetypes.public import DisplayList

formcontroller_transitions = (
    {'object_id'    : 'base_edit',
     'status'       : 'success',
     'context_type' : '',
     'button'       : 'reference_search',
     'action_type'  : 'traverse_to',
     'action_arg'   : 'string:base_edit'},

    {'object_id'    : 'base_edit',
     'status'       : 'success',
     'context_type' : '',
     'button'       : 'reference_add',
     'action_type'  : 'traverse_to',
     'action_arg'   : 'string:bibliography_list_edit'},

    {'object_id'    : 'base_edit',
     'status'       : 'success',
     'context_type' : '',
     'button'       : 'reference_delete',
     'action_type'  : 'traverse_to',
     'action_arg'   : 'string:bibliography_list_edit'},

    {'object_id'    : 'base_edit',
     'status'       : 'success',
     'context_type' : '',
     'button'       : 'reference_up',
     'action_type'  : 'traverse_to',
     'action_arg'   : 'string:bibliography_list_edit'},

    {'object_id'    : 'base_edit',
     'status'       : 'success',
     'context_type' : '',
     'button'       : 'reference_down',
     'action_type'  : 'traverse_to',
     'action_arg'   : 'string:bibliography_list_edit'},
                              )

FORMAT_MONTH_STYLES = DisplayList((
    ('m01', '01'),
    ('m1', '1'),
    ))
    
FORMAT_YEAR_STYLES = DisplayList((
    (None, 'xxxx'),
    ('yxx', 'xx'),
    ))

FORMAT_NUMBERSLISTS_STYLES = DisplayList((
    ('1, 3, 5-8, 10+', '1, 3, 5-8, 10+'),
    ('1; 3; 5-8; 10+', '1; 3; 5-8; 10+'),
    ))
        
FORMAT_NUMBERS_STYLES = DisplayList((
    (None, 'digital: 12'),
    ('roman', 'Roman: XII'),
    ('roman_lower', 'Roman: xii'),
    ))
        
FORMAT_GENERICSTRING_STYLES = DisplayList((
    (None, 'Rendering of the Value'),
    ('lower', 'rendering of the value'),
    ('upper', 'RENDERING OF THE VALUE'),
    ('ini', 'RotV'),
    ('ini_lower', 'rotv'),
    ('ini_upper', 'ROTV'),
    ('ini_dot', 'R.o.t.V.'),
    ('ini_dot_lower', 'r.o.t.v.'),
    ('ini_dot_upper', 'R.O.T.V.'),
    ('ini_dot_space', 'R. o. t. V.'),
    ('ini_dot_space_lower', 'r. o. t. v.'),
    ('ini_dot_space_upper', 'R. O. T. V.'),
    ('ini_space', 'R o t V'),
    ('ini_space_lower', 'r o t v'),
    ('ini_space_upper', 'R O T V'),
    ))

FORMAT_AUTHORS_LIST_ORDER = DisplayList((
    ('Smith','Smith'),
    ('Smith John','Smith John'),
    ('Smith John Edward','Smith John Edward'),
    ('John Smith','John Smith'),
    ('John Edward Smith','John Edward Smith'),
    ))