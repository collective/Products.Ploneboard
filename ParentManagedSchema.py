"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: ParentManagedSchema.py,v 1.4 2004/09/23 19:10:16 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import ImplicitAcquisitionWrapper
from Products.CMFCore.CMFCorePermissions import View

class ParentManagedSchema:
    """ mix-in class for AT content-types whose schema is managed by
        the parent container and retrieved through acquisition.
    """

    security = ClassSecurityInfo()    

    security.declareProtected(View, 'Schema')
    def Schema(self, schema_id):
        """ Retrieve schema from parent object. The client class should
            override the method as Schema(self) and then call his method
            of the baseclass with the corresponding schema_id.
        """

        # Schema() seems to be called during the construction phase when there is
        # not acquisition context. So we return the default schema itself.

        if not hasattr(self, 'aq_parent'): return self.schema

        # Otherwise get the schema from the parent collector through
        # acquisition and assign it to a volatile attribute for performance
        # reasons

        schema = getattr(self, '_v_schema', None)
        if schema is None:
            schema = self._v_schema = self.aq_parent.atse_getSchemaById(schema_id)

            for field in self._v_schema.fields():

                ##########################################################
                # Fake accessor and mutator methods
                ##########################################################

                name = field.getName()

                method = lambda self=self, name=name, *args, **kw: \
                         self.getField(name).get(self) 
                setattr(self, '_v_%s_accessor' % name, method )
                field.accessor = '_v_%s_accessor' % name
                field.edit_accessor = field.accessor

                method = lambda value,self=self, name=name, *args, **kw: \
                         self.getField(name).set(self, value) 
                setattr(self, '_v_%s_mutator' % name, method )
                field.mutator = '_v_%s_mutator' % name

                # Check if we need to update our own properties
                try:
                    value = field.get(self)  
                except:
                    field.set(self, field.default)

        return ImplicitAcquisitionWrapper(self._v_schema, self)

InitializeClass(ParentManagedSchema)
