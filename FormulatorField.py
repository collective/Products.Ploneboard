"""
provides access to formulator field registry

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from Products.Formulator.FieldRegistry import FieldRegistry

def getFieldFactory(fieldname):
    return FieldRegistry.get_field_class(fieldname)

def listFields():
    mapping = FieldRegistry.get_field_classes()
    field_types = mapping.keys()
    field_types.sort()
    return field_types


