import re
from AccessControl import Owned
from Acquisition import aq_get
from zLOG import LOG, INFO, WARNING
from Products.CMFCore.utils import getToolByName
from Acquisition import Explicit

_re_is_email = re.compile("^\s*([0-9a-zA-Z_&.+-]+!)*[0-9a-zA-Z_&.+-]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})\s*$")

TYPESMAP = {'boolean':('BooleanField', ''),
            'date':('DateTimeField', ''),
            'float':('FloatField', ''),
            'int':('IntegerField', ''),
            'lines':('LinesField', ''),
            'long':('IntegerField', ''),
            'string':('StringField', ''),
            'ustring':('StringField', ''),
            'text':('TextField', ''),
            'tokens':('LinesField', 'StringWidget'),
            'utext':('TextField',''),
            'utokens':('LinesField', 'StringWidget'),
            'ulines':('LinesField', ''),
            'selection':('StringField', 'SelectionWidget'),
            'multiple selection':('LinesField', 'MultiSelectionWidget'),
            }

def unique(sequence):
    """Make a sequence a tuple of unique items"""
    uniquedict = {}
    for v in sequence:
        uniquedict[v] = 1
    return tuple(uniquedict.keys())


def isEmail(email):
    return not not _re_is_email.match(email)


def log(summary='', text='', log_level=INFO):
    LOG('CMFMember Debug', log_level, summary, text)


def logException():
    """Dump an exception to the log"""
    import traceback
    import sys
    from zLOG import LOG, INFO, WARNING

    # sys.stdout.write('\n'.join(traceback.format_exception(*sys.exc_info())))
    
    s = sys.exc_info()[:2]  # don't assign the traceback to s (otherwise will generate a circular reference)
    if s[0] == None:
        summary = 'None'
    else:
        if type(s[0]) == type(''):
            summary = s[0]
        else:
            summary = str(s[1])

    LOG('CMFMember Debug', WARNING,
        summary,
        '\n'.join(traceback.format_exception(*sys.exc_info())))


def changeOwnership(object, user):
    """ # This is a replacement for Owned.py's changeOwnership function
    # Owned.changeOwnership is lame because when you change the owner of
    # a folder, you also end up changing the owner of all of the folder's
    # contents. """

    ### hmmm....wonder if this is the source of my cb_isMoveable problems. DWM
    new=Owned.ownerInfo(user)
    if new is None:
        return # Special user!
    old=aq_get(object, '_owner', None, 1)
    if old==new:
        return
    if old is Owned.UnownableOwner: return
    object._owner=new

class _MethodWrapper(Explicit):
    """Wrapper to create instance methods"""
    def __init__(self, f): self.__f = f
    def __call__(self, *args, **kw):
        return self.__f(self.aq_parent, *args, **kw)


def userFolderDelUsers(self, names):
    """Override acl_users user deletion"""
    memberdata = getToolByName(self, 'portal_memberdata')
    memberdata.manage_delObjects(names)


class ContentPermMap(dict):

    def __setitem__(self, key, value):
        if key in self:
            values = self[key]
            if isinstance( values, str):
                values = [values]
            elif isinstance(values, tuple):
                values = list(value)

            if value is None or values is None:
                values = None
            elif isinstance(value, str ):
                values.append( value )
            elif isinstance(value, (list, tuple)):
                values.extend( list(value ) )
            else:
                raise SyntaxError("Unknown %r %r%"(values, value))
            value = values

        super(ContentPermMap, self).__setitem__(key, value)


def separateTypesByPerm( at_types,
                         content_types,
                         constructors,
                         permission_map ):

    res = {}

    default_perm = None
    used_types = []


    for permission in permission_map:
        portal_types = permission_map[ permission ]

        if portal_types is None:
            # default perm
            default_perm = permission
            continue

        types_for_perm = res.setdefault( permission, [])

        for idx, atype in enumerate(at_types):
            pt = atype['klass'].portal_type
            if pt in portal_types:
                assert pt not in used_types
                types_for_perm.append(
                    ( content_types[idx],
                      constructors[idx] )
                    )
                used_types.append( pt )


    if not default_perm:
        return res

    # handle default add permission 
    types_for_perm = res.setdefault( default_perm , [] )

    for idx, atype in enumerate(at_types ):
        pt = atype['klass'].portal_type
        if not pt in used_types:
            types_for_perm.append(
                ( content_types[idx],
                  constructors[idx] )
                )

    return res
