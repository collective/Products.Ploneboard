from Products.Archetypes.public import *
from Products.ATSchemaEditorNG.ParentManagedSchema import ParentManagedSchema
from Products.ATSchemaEditorNG.SchemaEditor import SchemaEditor
from Products.ATSchemaEditorNG import util
from Products.CMFCore.utils import getToolByName

schema = BaseSchema
schema1= BaseSchema + Schema( StringField('additionalField'), )

class Container(SchemaEditor, BaseFolder):
    """
    Container to act as host for schema editing.
    """
    
    portal_type = "Container"

    def manage_afterAdd(self, item, container):
        """ """

        # do not show metadata fieldset
        self.atse_registerObject( Target1, ('metadata', ))
        self.schema_editor_tool.atse_registerObject( Target1, ('metadata', ))
        BaseFolder.manage_afterAdd(self, item, container)

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
