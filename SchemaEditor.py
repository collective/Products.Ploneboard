# -*- coding: iso-8859-1

"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
and Contributors
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: SchemaEditor.py,v 1.24 2004/10/25 16:05:53 ajung Exp $
"""

import re

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import ImplicitAcquisitionWrapper
from BTrees.OOBTree import OOBTree
from Products.CMFCore.CMFCorePermissions import *
from Products.Archetypes.public import DisplayList, BaseFolderSchema
from Products.Archetypes.Field import *
from Products.Archetypes.Widget import *
from ManagedSchema import ManagedSchema

import util
from config import ManageSchemaPermission

id_regex = re.compile('^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$')
allowed = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_/ ().,:;#+*=&%$§!'

def remove_unallowed_chars(s):
    return ''.join([c  for c in s  if c in allowed])

TYPE_MAP = {
'StringField':     StringField,
'IntegerField':    IntegerField,
'FloatField':      FloatField,
'FixedPointField': FixedPointField,
'BooleanField':    BooleanField,
'LinesField':      LinesField,
'DateTimeField':   DateTimeField,
'ReferenceField':  ReferenceField,
}

WIDGET_MAP = {
'String':      StringWidget(),
'Select':      SelectionWidget(format='select'),
'Flex':        SelectionWidget(format='flex'),
'Radio':       SelectionWidget(format='radio'),
'Textarea':    TextAreaWidget(),
'Calendar':    CalendarWidget(),
'Boolean':     BooleanWidget(),
'MultiSelect': MultiSelectionWidget(),
'Keywords':    KeywordWidget(),
'Richtext':    RichWidget(),
'Password':    PasswordWidget(),
'Lines':       LinesWidget(),
'Visual':      VisualWidget() ,
'Epoz':        EpozWidget(),
'Image':       ImageWidget(),
'Integer':     IntegerWidget(),
'Decimal':     DecimalWidget(),
'Reference':   ReferenceWidget(),
'Picklist':    PicklistWidget(),
'InAndOut':    InAndOutWidget(),
}

# support for ATReferenceBrowserWidget
HAS_ATREF_WIDGET = False
try:
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
    WIDGET_MAP['ReferenceBrowserWidget'] = ReferenceBrowserWidget()
    HAS_ATREF_WIDGET = True
    
except ImportError:
    pass

class SchemaEditorError(Exception): pass

class SchemaEditor:
    """ a simple TTW editor for Archetypes schemas """

    security = ClassSecurityInfo()

    security.declareProtected(ManageSchemaPermission, 'atse_init')
    def atse_init(self):
        """ init everything """

        # only for compat reasons
        return

    def _clear(self, safe=False):
        if not safe:
            self._schemas = OOBTree()   # schema_id -> ManagedSchema instance
            self._obj_ptype = []

        # safe update
        else:
            if not hasattr(self, '_schemas'):
                self._schemas = OOBTree()

            if not hasattr(self, '_obj_ptype'):
                self._obj_ptype = []

    security.declareProtected(ManageSchemaPermission, 'atse_registerSchema')
    def atse_registerSchema(self, 
                            schema_id,
                            schema,     
                            filtered_schemas=(), 
                            undeleteable_fields=(), 
                            undeleteable_schematas=('default', 'metadata'), 
                            domain='plone'):

        # staying in sync
        self._clear(safe=True)
            
        if self._schemas.has_key(id):
            raise SchemaEditorError('Schema with id "%s" already exists' % id)
    
        S = ManagedSchema(schema.fields())
        S._filtered_schemas = filtered_schemas
        S._undeleteable_fields = undeleteable_fields
        S._undeleteable_schematas = undeleteable_schematas 
        S._i18n_domain = domain
        self._schemas[schema_id] = S

    def atse_registerObject(self, obj,
                            filtered_schemas=(), 
                            undeleteable_fields=(), 
                            undeleteable_schematas=('default', 'metadata'), 
                            domain='plone'):
        """
        Using that method you can register an object.
        Information needed are extracted from it. The Schema id
        is set to the portal type of the object.
        """

        if not hasattr(obj, 'portal_type'):
            raise Exception, 'Object %s is not an valid input' % str(obj)

        # avoiding update problems
        self._clear(safe=True)

        schema = getattr(obj, 'schema')
        ptype = getattr(obj, 'portal_type')

        if not (ptype in self._obj_ptype):
            self._obj_ptype.append(ptype)

        # do nothing if object is already there
        # XXX refresh schema
        else: return
            
        self.atse_registerSchema(ptype, schema,
                                 filtered_schemas,
                                 undeleteable_fields,
                                 undeleteable_schematas,
                                 domain)

    security.declareProtected(ManageSchemaPermission, 'atse_unregisterSchema')
    def atse_unregisterSchema(self, schema_id):
        """ unregister schema """
        if not self._schemas.has_key(schema_id):
            raise SchemaEditorError('No such schema: %s' % schema_id)
        del self._schemas[schema_id]

    security.declareProtected(ManageSchemaPermission, 'atse_reRegisterSchema')
    def atse_reRegisterSchema(self, schema_id, schema):
        """ re-registering schema """

        self.atse_unregisterSchema(schema_id)
        self.atse_registerSchema(schema_id, schema)
        self._p_changed = 1
        
    security.declareProtected(ManageSchemaPermission, 'atse_reRegisterObject')
    def atse_reRegisterObject(self, object):
        """ re-registering object """

        self.atse_unregisterSchema(object.portal_type)
        self._obj_ptype.remove(object.portal_type)
        self.atse_registerObject(object)
        self._p_changed = 1

    security.declareProtected(View, 'atse_getSchemaById')
    def atse_getSchemaById(self, schema_id):
        """ return a schema by its schema_id """
        if not self._schemas.has_key(schema_id):
            raise SchemaEditorError('No such schema: %s' % schema_id)
        return self._schemas[schema_id]

    security.declareProtected(View, 'atse_getSchemaById')
    def atse_getRegisteredSchemata(self):
        """
        Returns all registered schemata
        """

        return self._schemas.keys()

    security.declareProtected(View, 'atse_getSchemaById')
    def atse_selectRegisteredSchema(self, schema_template, REQUEST=None):
        """
        Redirection
        """

        req = REQUEST or self.REQUEST
        sel = req.form['selection']
        return util.redirect(req.RESPONSE, schema_template,
                      self.translate('Now editing schema for %s' % sel), schema_id=sel)

    security.declareProtected(View, 'atse_isSchemaRegistered')
    def atse_isSchemaRegistered(self, schema_id):
        """ returns True if schema exists """
        return self._schemas.has_key(schema_id) > 0

    security.declareProtected(View, 'atse_getDefaultSchema')
    def atse_getDefaultSchema(self):
        """ returns the first schema in list """

        if self._schemas.items():
            return self._schemas.items()[0][1]

        # XXX urgh
        return BaseFolderSchema()

    security.declareProtected(View, 'atse_getDefaultSchemaId')
    def atse_getDefaultSchemaId(self):
        """ returns default schema id """

        if self._schemas.items():
            return self._schemas.items()[0][0]

        return ''

    security.declareProtected(View, 'atse_getSchemataNames')
    def atse_getSchemataNames(self, schema_id, filter=True):
        """ return names of all schematas """

        S = self.atse_getSchemaById(schema_id)
        if filter:
            return [n for n in S.getSchemataNames() if not n in S._filtered_schemas]
        else:
            return [n for n in s.getSchemataNames()]

    security.declareProtected(View, 'atse_getSchemata')
    def atse_getSchemata(self, schema_id, name):
        """ return a schemata given by its name """
        S = self.atse_getSchemaById(schema_id)
        s = ManagedSchema()
        for f in S.getSchemataFields(name): # Can't we create a copy?
            s.addField(f)
        return ImplicitAcquisitionWrapper(s, self)

    ######################################################################
    # Add/remove schematas
    ######################################################################

    security.declareProtected(ManageSchemaPermission, 'atse_addSchemata')
    def atse_addSchemata(self, schema_id, schema_template, name, RESPONSE=None):
        """ add a new schemata """

        S = self.atse_getSchemaById(schema_id)

        if not name:
            raise SchemaEditorError(self.translate('atse_empty_name', default='Empty ID given'))

        if name in S.getSchemataNames():
            raise SchemaEditorError(self.translate('atse_exists', {schemata:name},
                                    'Schemata "$schemata" already exists'))
        if not id_regex.match(name):
            raise SchemaEditorError(self.translate('atse_invalid_id_for_schemata', {'schemata':name},
                                    '"$schemata" is an invalid ID for a schemata'))

        S.addSchemata(name)
        self._schemas[schema_id] = S

        util.redirect(RESPONSE, schema_template,
                      self.translate('atse_added', default='Schemata added'), schemata=name)

    security.declareProtected(ManageSchemaPermission, 'atse_delSchemata')
    def atse_delSchemata(self, schema_id, schema_template, name, RESPONSE=None):
        """ delete a schemata """

        S = self.atse_getSchemaById(schema_id)

        if name in S._undeleteable_schematas: 
            raise SchemaEditorError(self.translate('atse_can_not_remove_schema', 
                                    default='Can not remove this schema because it is protected from deletion'))

        if len(self.atse_getSchemataNames(schema_id, True)) == 1: 
            raise SchemaEditorError(self.translate('atse_can_not_remove_last_schema', 
                                    default='Can not remove the last schema'))

        for field in S.getSchemataFields(name): 
            if field.getName() in S._undeleteable_fields:
                raise SchemaEditorError(self.translate('atse_schemata_contains_undeleteable_fields', 
                                        default='The schemata contains fields that can not be deleted'))

        
        S.delSchemata(name)
        self._schemas[schema_id] = S
        util.redirect(RESPONSE, 
                      schema_template,
                      self.translate('atse_deleted', 
                                     default='Schemata deleted'),   
                                     schemata=self.atse_getSchemataNames(schema_id))

    ######################################################################
    # Field manipulation
    ######################################################################

    security.declareProtected(ManageSchemaPermission, 'atse_delField')
    def atse_delField(self, schema_id, schema_template, name, RESPONSE=None):
        """ remove a field from the  schema"""

        S = self.atse_getSchemaById(schema_id)

        if name in S._undeleteable_fields:
            raise SchemaEditorError(self.translate('atse_field_not_deleteable',
                                            {'name' : name},
                                            'field "$name" can not be deleted because it is protected from deletion',   
                                            ))

        old_schemata = S
        S.delField(name)    

        if old_schemata in S.getSchemataNames(): # Schematas disappear if they are empty
            return_schemata = old_schemata
        else:
            return_schemata = self.atse_getSchemataNames(schema_id, True)[0]
	
        self._schemas[schema_id] = S
        util.redirect(RESPONSE, 
                      schema_template,
                      self.translate('atse_field_deleted', 
                                     default='Field deleted'), 
                                     schemata=return_schemata)

    security.declareProtected(ManageSchemaPermission, 'atse_update')
    def atse_update(self, schema_id, schema_template, fielddata,  REQUEST, RESPONSE=None):
        """ update a single field"""

        S = self.atse_getSchemaById(schema_id)
        R = REQUEST.form
        FD = fielddata

        ## ATT: this should go into a dedicated method
        if R.has_key('add_field'):
            if not R['name']:
                raise SchemaEditorError(self.translate('atse_empty_field_name', 
                                                default='Field name is empty'))

            if not id_regex.match(R['name']):
                raise SchemaEditorError(self.translate('atse_not_a_valid_id', 
                                                {'id' : R['name']},
                                                '"$id" is not a valid ID'))

            if R['name'] in [f.getName() for f in S.fields()]:
                raise SchemaEditorError(self.translate('atse_field_already_exists', 
                                               {'id' : R['name']},
                                               '"$id" exists already'))

            fieldset = FD.schemata    
            field = StringField(R['name'], schemata=fieldset, widget=StringWidget)
            S.addField(field)
            self._schemas[schema_id] = S
            util.redirect(RESPONSE, schema_template,
                          self.translate('atse_field_added', 
                                         default='Field added'), 
                                         schemata=fieldset, 
                                         field=R['name'])
            return            

        field = TYPE_MAP.get(FD.type, None)
        if not field:
            raise SchemaEditorError(self.translate('atse_unknown_field', 
                                              {'field' : FD.field},
                                             'unknown field type: $field')) 

        D = {}    # dict to be passed to the field constructor
        D['default'] = FD.get('default', '')
        D['schemata'] = FD.schemata
        D['createindex'] = FD.get('createindex', 0)
         
        # build widget
        widget = WIDGET_MAP.get(FD.widget, None)
        if not widget:
            raise SchemaEditorError(self.translate('atse_unknown_widget', 
                                                  {'widget' : FD.widget},
                                                  'unknown widget type: $widget'))

        # support for relations
        D['relationship'] = FD.get('relationship', 'defaultRelation')

        if FD.has_key('widgetsize'):
            widget.size = FD.widgetsize
            widget.rows = 5
            widget.cols = 60
        
        elif FD.has_key('widgetcols') and FD.has_key('widgetrows'):
            widget.rows = FD['widgetrows']
            widget.cols = FD['widgetcols']
            widget.size = 60
        else:
            raise SchemaEditorError

        # setting visibility of field
        widget.visible = {'edit' : 'visible', 'view' : 'visible'}
        if not FD.has_key('visible_edit'):
            widget.visible['edit'] = 'invisible'

        if not FD.has_key('visible_view'):
            widget.visible['view'] = 'invisible'

        # Validators
        if FD.has_key('validators'):
            validators = tuple([v.strip() for v in FD['validators'].split(',')])
            if validators:
                widget.validators = validators
            
        widget.label = FD.label
        widget.label_msgid = 'label_' + FD.label
        widget.i18n_domain = S._i18n_domain

        D['widget'] = widget

        # build DisplayList instance for SelectionWidgets
        if FD.widget in ('Radio', 'Select', 'MultiSelect', 'Flex', 'Picklist', 'InAndOut'):
            vocab = FD.get('vocabulary', [])

            # The vocabulary can either be a list of string of 'values'
            # or a list of strings 'key|value' or a list with *one*
            # string 'method:<methodname>'. 'method:<methodname>' is used
            # specify a method that is called to retrieve a DisplayList
            # instance

            if len(vocab) == 1 and vocab[0].startswith('method:'):
                dummy,method = vocab[0].split(':')
                D['vocabulary'] = method.strip()
            else:
                l = []
                for line in vocab:
                    line = line.strip()
                    if not line: continue
                    if '|' in line:
                        k,v = line.split('|', 1)
                    else:
                        k = v = line

                    k = remove_unallowed_chars(k)
                    l.append( (k,v))

                D['vocabulary'] = DisplayList(l)

        D['required'] = FD.get('required', 0)

        newfield = field(FD.name, **D)
        S.replaceField(FD.name, newfield)
        self._schemas[schema_id] = S

        util.redirect(RESPONSE, schema_template,
                      self.translate('atse_field_changed', default='Field changed'), 
                      schema_id=schema_id,
                      schemata=FD.schemata, 
                      field=FD.name)

    ######################################################################
    # Moving schematas and fields
    ######################################################################

    security.declareProtected(ManageSchemaPermission, 'atse_schemataMoveLeft')
    def atse_schemataMoveLeft(self, schema_id, schema_template, name, RESPONSE=None):
        """ move a schemata to the left"""
        S = self.atse_getSchemaById(schema_id)
        S.moveSchemata(name, -1)
        self._schemas[schema_id] = S
        util.redirect(RESPONSE, schema_template,
                      self.translate('atse_moved_left', default='Schemata moved to left'), 
                      schema_id=schema_id,
                      schemata=name)

    security.declareProtected(ManageSchemaPermission, 'atse_schemataMoveRight')
    def atse_schemataMoveRight(self, schema_id, schema_template, name, RESPONSE=None):
        """ move a schemata to the right"""
        S = self.atse_getSchemaById(schema_id)
        S.moveSchemata(name, 1)
        self._schemas[schema_id] = S
        util.redirect(RESPONSE, schema_template,
                      self.translate('atse_moved_right', default='Schemata moved to right'), 
                      schema_id=schema_id,
                      schemata=name)

    security.declareProtected(ManageSchemaPermission, 'atse_fieldMoveLeft')
    def atse_fieldMoveLeft(self, schema_id, schema_template, name, RESPONSE=None):
        """ move a field of a schemata to the left"""
        S = self.atse_getSchemaById(schema_id)
        S.moveField(name, -1)
        self._schemas[schema_id] = S
        util.redirect(RESPONSE, schema_template,
                      self.translate('atse_field_moved_up', default='Field moved up'), 
                      schemata=S[name].schemata, 
                      schema_id=schema_id,
                      field=name)

    security.declareProtected(ManageSchemaPermission, 'atse_fieldMoveRight')
    def atse_fieldMoveRight(self, schema_id, schema_template, name, RESPONSE=None):
        """ move a field of a schemata to the right"""
        S = self.atse_getSchemaById(schema_id)
        S.moveField(name, 1)
        self._schemas[schema_id] = S
        util.redirect(RESPONSE, schema_template, 
                      self.translate('atse_field_moved_down', default='Field moved down'), 
                      schemata=S[name].schemata, 
                      schema_id=schema_id,
                      field=name)

    security.declareProtected(ManageSchemaPermission, 'atse_changeSchemataForField')
    def atse_changeSchemataForField(self, schema_id, schema_template, name, schemata_name, RESPONSE=None):
        """ move a field from the current fieldset to another one """
        S = self.atse_getSchemaById(schema_id)
        S.changeSchemataForField(name, schemata_name)
        self._schemas[schema_id] = S
        util.redirect(RESPONSE, schema_template,
                      self.translate('atse_field_moved', default='Field moved to other fieldset'), 
                      schemata=schemata_name, 
                      schema_id=schema_id,
                      field=name)

    ######################################################################
    # Hook for UI
    ######################################################################

    security.declareProtected(ManageSchemaPermission, 'atse_getField')
    def atse_getField(self, schema_id, name):
        """ return a field by its name """
        S = self.atse_getSchemaById(schema_id)
        return S[name]

    security.declareProtected(ManageSchemaPermission, 'atse_getFieldType')
    def atse_getFieldType(self, field):
        """ return the type of a field """
        return field.__class__.__name__
    
    security.declareProtected(ManageSchemaPermission, 'atse_formatVocabulary')
    def atse_formatVocabulary(self, field):
        """ format the DisplayList of a field to be displayed
            within a textarea.
        """

        if isinstance(field.vocabulary, str):
            return 'method:' + field.vocabulary

        l = []
        for k in field.vocabulary:
            v = field.vocabulary.getValue(k)
            if k == v: l.append(k)
            else: l.append('%s|%s' % (k,v))
        return '\n'.join(l)

    security.declareProtected(ManageSchemaPermission, 'atse_schema_baseclass')
    def atse_schema_baseclass(self, schema_id):
        """ return name of baseclass """
        S = self.atse_getSchemaById(schema_id)
        return S.__class__.__name__

    ######################################################################
    # [spamies] Helper methods for maintenance and widget access
    ######################################################################

    security.declareProtected(ManageSchemaPermission, 'atse_isFieldVisible')
    def atse_isFieldVisible(self, fieldname, mode='view', schema_id=None):
        """
        Returns True if the given field is visible
        in the given mode. Default is view.
        """

        if not schema_id:
            schema_id = self.atse_getDefaultSchemaId()
            
        field = self.atse_getField(schema_id, fieldname)
        if hasattr(field.widget, 'visible'):
            if field.widget.visible.get(mode) == 'invisible':
                return False
            else: return True

        # always True if we've found nothing
        return True

    security.declareProtected(ManageSchemaPermission, 'atse_editorCanUpdate')
    def atse_editorCanUpdate(self, portal_type):
        """
        Returns True if an object was registered and
        its portal_type could be saved.
        """

        if hasattr(self, '_obj_ptype'):
           if portal_type and \
                  (portal_type in getattr(self, '_obj_ptype')):
               return True

        return False

    security.declareProtected(ManageSchemaPermission, 'atse_updateManagedSchemas')
    def atse_updateManagedSchema(self,
                                 portal_type,
                                 schema_template,
                                 REQUEST=None, RESPONSE=None):
        
        """
        Update stored issue schema for all managed schemas.
        That can only done, if an complete object was registered.
        """

        # we absolutely need to have portal_type
        if not self.atse_editorCanUpdate(portal_type):
            return util.redirect(RESPONSE, schema_template,
                                 self.translate('Can not determine portal_type of managed objects (%s)...' \
                                                % portal_type))

        # we assume that the schema name is the same as the portal_type
        schema = self.atse_getSchemaById(portal_type)

        # gettin' objects and updating them
        objects = [ o.getObject() for o in self.portal_catalog.searchResults(portal_type=portal_type)]

        # ParentManagedSchema is refreshing the schema,
        # if the _v_ variable is None...
        for obj in objects:
            if hasattr(obj, '_v_schema'):
                delattr(obj, '_v_schema')
                obj._p_changed = 1

        # XXX do translation
        return util.redirect(RESPONSE, schema_template,
                      self.translate('Updated objects of type %s successfully' % portal_type))

InitializeClass(SchemaEditor)
