##########################################################################
#                                                                        #
#              copyright (c) 2004 Belgian Science Policy                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" File containing the displaylists for the different string formats 
    (these lists are used in the selection boxes in formatting files)
"""

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

LISTING_VALUES = DisplayList((
    ('bulleted', 'Bulleted list'),
    ('ordered', 'Ordered list'),
    ('lines', 'Simple lines list'),
    ('table', 'Table listing'),
    ))

FORMAT_MONTH_STYLES = DisplayList((
    ('m01', '01'),
    ('m1', '1'),
    ))
    
FORMAT_YEAR_STYLES = DisplayList((
    ('', 'xxxx'),
    ('yxx', 'xx'),
    ))

FORMAT_NUMBERSLISTS_STYLES = DisplayList((
    ('', '1, 3, 5-8, 10+'),
    ('semicolon', '1; 3; 5-8; 10+'),
    ))
        
FORMAT_NUMBERS_STYLES = DisplayList((
    ('', 'digital: 12'),
    ('roman', 'Roman: XII'),
    ('roman_lower', 'Roman: xii'),
    ))
        
FORMAT_GENERICSTRING_STYLES = DisplayList((
    ('', 'Rendering of the Value'),
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

FORMAT_TITLE_STYLES = DisplayList((
    ('', 'Rendering of the Value'),
    ('lower', 'rendering of the value'),
    ('upper', 'RENDERING OF THE VALUE'),
    ))

FORMAT_AUTHORS_LIST_ORDER = DisplayList((
    ('first middle last', 'Firstname Middlename Lastname (John Edward Smith)'),
    ('first last','Firstname Lastname (John Smith)'),
    ('last','Lastname (Smith)'),
    ('last first','Lastname Firstname (Smith John)'),
    ('last, first','Lastname, Firstname (Smith, John)'),
    ('last first middle','Lastname Firstname Middlename (Smith John Edward)'),
    ('last, first middle','Lastname, Firstname Middlename (Smith, John Edward)'),
    ))

DEFAULT_REFS_DISPLAY = '%A: "%T" - %P (%Y).'

CUSTOM_DISPLAY_CONVENTIONS = (
    ('A', 'Author'),
    ('T', 'Title'),
    ('m', 'Publication_month'),
    ('y', 'Publication_year'),
    ('J', 'Journal'),
    ('I', 'Institution'),
    ('O', 'Organization'),
    ('B', 'Booktitle'),
    ('p', 'Pages'),
    ('v', 'Volume'),
    ('n', 'Number'),
    ('E', 'Editor(s)'),
    ('P', 'Publisher'),
    ('a', 'Address'),
    ('i', 'Pmid'),
    ('e', 'Edition'),
    ('h', 'Howpublished'),
    ('c', 'Chapter'),
    ('S', 'School'),
    ('r', 'Preprint sever'),
    ('s', 'Series'),
    ('%', '"%" sign'),
    )

OLD_CUSTOM_DISPLAY_CONVENTIONS_ROWS = (
    ('%A', '%p', '%h'),
    ('%T', '%v', '%c'),
    ('%m', '%n', '%s'),
    ('%y', '%E', '%r'),
    ('%J', '%p', '%s'),
    ('%I', '%a', '%%'),
    ('%O', '%i', ''),
    ('%B', '%e', ''),
    )

CUSTOM_DISPLAY_CONVENTIONS_ROWS = (
    ('%A', '%O', '%p', '%s'),
    ('%T', '%B', '%a', '%r'),
    ('%m', '%p', '%i', '%s'),
    ('%y', '%v', '%e', '%%'),
    ('%J', '%n', '%h', ''),
    ('%I', '%E', '%c', ''),
    )