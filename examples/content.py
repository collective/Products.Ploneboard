from Products.Archetypes.public import *
from Products.ATSchemaEditorNG.ParentManagedSchema import ParentManagedSchema
from Products.ATSchemaEditorNG.SchemaEditor import SchemaEditor
from Products.ATSchemaEditorNG import util
from Products.CMFCore.utils import getToolByName

schema = BaseSchema
schema1= BaseSchema + Schema( StringField('additionalField'), )

class Container(SchemaEditor, BaseFolder):
    """ Container to act as host for schema editing"""

    def update_all_schemas(self, meta_type='Target1', return_to=None, REQUEST=None, RESPONSE=None):
        """ update stored issue schema for all issues """

        schema = self.atse_getSchema()

        objs = [ ( obj, setattr(obj, '_v_schema', None) ) for obj in self.objectValues(spec=meta_type) \
                 if hasattr(obj, '_v_schema') ]
        
        obj = objs[0][0]

        if len(objs):
            if return_to:
                util.redirect(RESPONSE, return_to,
                              self.translate('schema_updated'))
            else:
                util.redirect(RESPONSE, '%s_schema_editor'%obj.portal_type,
                              self.translate('schema_updated'))
        else:
            util.redirect(RESPONSE, 'atse_editor',
                          self.translate('%s_updated' %obj.portal_type, '%s updated'%obj.archetype_name))

    def manage_afterAdd(self, item, container):
        """ """
        att = getToolByName(self, "archetype_tool")
        self.atse_init( Target1.schema, Target1.meta_type) 

registerType(Container)

class Target1(ParentManagedSchema, BaseContent):
    """ Target content type to edit schema on """

    meta_type = portal_type = "Target1"
    schema = schema1

registerType(Target1)

class Target2(ParentManagedSchema, BaseContent):
    """ Target content type to edit schema on """

    meta_type = portal_type = "Target2"


registerType(Target2)
