""" File containing the displaylists for the different string formats (these lists are used in the selection boxes in formatting files)"""

from Products.Archetypes.public import DisplayList

FORMAT_MONTH_STYLES = DisplayList((
    ('m01', '01'),
    ('m1', '1'),
    ))
    
FORMAT_YEAR_STYLES = DisplayList((
    ('19xx', '19xx'),
    ('xx', 'xx'),
    ))

FORMAT_NUMBERSLISTS_STYLES = DisplayList((
    ('1, 3, 5-8, 10+', '1, 3, 5-8, 10+'),
    ('1; 3; 5-8; 10+', '1; 3; 5-8; 10+'),
    ))
        
FORMAT_NUMBERS_STYLES = DisplayList((
    ('digital: 12', 'digital: 12'),
    ('Roman: XII', 'Roman: XII'),
    ('Roman: xii', 'Roman: xii'),
    ))
        
FORMAT_GENERICSTRING_STYLES = DisplayList((
    ('Format of the Field', 'Format of the Field'),
    ('FORMAT OF THE FIELD', 'FORMAT OF THE FIELD'),
    ('format of the field', 'format of the field'),
    ('F.o.t.F.', 'F.o.t.F.'),
    ('FotF', 'FotF'),
    ('F.O.T.F.', 'F.O.T.F.'),
    ('FOTF', 'FOTF'),
    ('f.o.t.f.', 'f.o.t.f.'),
    ('fotf', 'fotf'),
    ))

FORMAT_AUTHORS_LIST_ORDER = DisplayList((
    ('Smith','Smith'),
    ('Smith John','Smith John'),
    ('Smith John Edward','Smith John Edward'),
    ('John Smith','John Smith'),
    ('John Edward Smith','John Edward Smith'),
    ))