# -*- coding: iso-8859-1

"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: SchemaEditor.py,v 1.15 2004/09/23 18:36:55 ajung Exp $
"""

import re

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import ImplicitAcquisitionWrapper
from BTrees.OOBTree import OOBTree
from Products.CMFCore.CMFCorePermissions import *
from Products.Archetypes.public import DisplayList
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

class SchemaEditorError(Exception): pass

class SchemaEditor:
    """ a simple TTW editor for Archetypes schemas """

    security = ClassSecurityInfo()

    security.declareProtected(ManageSchemaPermission, 'atse_init')
    def atse_init(self):
        """ init everything """
        self._clear()

    def _clear(self):
        self._schemas = OOBTree()   # schema_id -> ManagedSchema instance

    security.declareProtected(ManageSchemaPermission, 'atse_registerSchema')
    def atse_registerSchema(self, 
                            schema_id,
                            schema,     
                            filtered_schemas=(), 
                            undeleteable_fields=(), 
                            undeleteable_schematas=('default', 'metadata'), 
                            domain='plone'):

        if self._schemas.has_key(id):
            raise SchemaEditorError('Schema with id "%s" already exists' % id)
    
        S = ManagedSchema(schema.fields())
        S._filtered_schemas = filtered_schemas
        S._undeleteable_fields = undeleteable_fields
        S._undeleteable_schematas = undeleteable_schematas 
        S._i18n_domain = domain
        self._schemas[schema_id] = S

    security.declareProtected(ManageSchemaPermission, 'atse_unregisterSchema')
    def atse_unregisterSchema(self, schema_id):
        """ unregister schema """
        if not self._schemas.has_key(schema_id):
            raise SchemaEditorError('No such schema: %s' % schema_id)
        del self._schemas[schema_id]
        

    security.declareProtected(View, 'atse_getSchemaById')
    def atse_getSchemaById(self, schema_id):
        """ return a schema by its schema_id """
        if not self._schemas.has_key(schema_id):
            raise SchemaEditorError('No such schema: %s' % schema_id)
        return self._schemas[schema_id]

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
                                                  {'widget' : d.widget},
                                                  'unknown widget type: $widget'))

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

        widget.visible = 1
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

InitializeClass(SchemaEditor)
