# -*- coding: iso-8859-1 -*-

"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
and Contributors
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: interfaces.py,v 1.2 2004/12/10 07:17:04 ajung Exp $
"""

from Interface import Interface

class IParentManagedSchema(Interface):
    """ mix-in class for AT content-types whose schema is managed by
        the parent container and retrieved through acquisition.
    """

    def _wrap_schema(schema):
        """ return aquisition wrapped schema """

    def _lookupChanges(atse_schema_id):
        """ Checks if schema has changed """

    def Schema(schema_id=None):
        """ Retrieve schema from parent object. The client class should
            override the method as Schema(self) and then call his method
            of the baseclass with the corresponding schema_id.
        """

class ISchemaEditor(Interface):
    """ a simple TTW editor for Archetypes schemas """
    
    def atse_init():
        """ only for compat reasons """

    def _clear(safe=False):
        """ emply btree schema store and object parent type """

    def atse_registerSchema( schema_id, schema, filtered_schemas=(), 
                             undeleteable_fields=(), 
                             undeleteable_schematas=('default', 'metadata'), 
                             domain='plone'):
        """ registers a working copy of a schema """

    def atse_registerObject( obj,
                             filtered_schemas=(), 
                             undeleteable_fields=(), 
                             undeleteable_schematas=('default', 'metadata'), 
                             domain='plone'):
        """
        Using that method you can register an object.
        Information needed are extracted from it. The Schema id
        is set to the portal type of the object.
        """

    def atse_unregisterSchema(schema_id):
        """ unregister schema """

    def atse_reRegisterSchema(schema_id, schema):
        """ re-registering schema """

    def atse_reRegisterObject(object):
        """ re-registering object """

    def atse_getSchemaById(schema_id):
        """ return a schema by its schema_id """

    def atse_getRegisteredSchemata():
        """
        Returns all registered schemata
        """
        
    def atse_selectRegisteredSchema(schema_template, REQUEST=None):
        """
        Redirection
        """
        
    def atse_isSchemaRegistered(schema_id):
        """ returns True if schema exists """

    def atse_getDefaultSchema():
        """ returns the first schema in list """

    def atse_getDefaultSchemaId():
        """ returns default schema id """

    def atse_getSchemataNames( schema_id, filter=True):
        """ return names of all schematas """

    def atse_getSchemata( schema_id, name):
        """ return a schemata given by its name """

    def atse_addSchemata( schema_id, schema_template, name, RESPONSE=None):
        """ add a new schemata """

    def atse_delSchemata( schema_id, schema_template, name, RESPONSE=None):
        """ delete a schemata """

    def atse_delField( schema_id, schema_template, name, RESPONSE=None):
        """ remove a field from the  schema"""

    def atse_update( schema_id, schema_template, fielddata,  REQUEST, RESPONSE=None):
        """ update a single field"""

    def atse_schemataMoveLeft( schema_id, schema_template, name, RESPONSE=None):
        """ move a schemata to the left"""

    def atse_schemataMoveRight( schema_id, schema_template, name, RESPONSE=None):
        """ move a schemata to the right"""

    def atse_fieldMoveLeft( schema_id, schema_template, name, RESPONSE=None):
        """ move a field of a schemata to the left"""

    def atse_fieldMoveRight( schema_id, schema_template, name, RESPONSE=None):
        """ move a field of a schemata to the right"""

    def atse_changeSchemataForField( schema_id, schema_template, name, schemata_name, RESPONSE=None):
        """ move a field from the current fieldset to another one """

    def atse_getField( schema_id, name):
        """ return a field by its name """

    def atse_getFieldType( field):
        """ return the type of a field """

    def atse_formatVocabulary( field):
        """ format the DisplayList of a field to be displayed
            within a textarea.
        """
        
    def atse_schema_baseclass( schema_id):
        """ return name of baseclass """

    def atse_isFieldVisible( fieldname, mode='view', schema_id=None):
        """
        Returns True if the given field is visible
        in the given mode. Default is view.
        """

    def atse_editorCanUpdate( portal_type):
        """
        Returns True if an object was registered and
        its portal_type could be saved.
        """

    def atse_updateManagedSchema( portal_type,
                                  schema_template,
                                  REQUEST=None, RESPONSE=None):
        """
        Update stored issue schema for all managed schemas.
        That can only done, if an complete object was registered.
        """
