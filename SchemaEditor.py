# -*- coding: iso-8859-1

"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 Tübingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: SchemaEditor.py,v 1.1 2004/09/12 07:27:21 ajung Exp $
"""

import re

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import ImplicitAcquisitionWrapper
from Products.CMFCore.CMFCorePermissions import *
from Products.Archetypes.public import DisplayList
from Products.Archetypes.Field import *
from Products.Archetypes.Widget import *
from ManagedSchema import ManagedSchema

import util
from config import ManageSchema

UNDELETEABLE_FIELDS = ('title', 'description', 'classification', 'topic', 'importance', 'contact_email', 'contact_name')

id_regex = re.compile('^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$')
allowed = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_/ ().,:;#+*=&%$§!'

def remove_unallowed_chars(s):
    return ''.join([c  for c in s  if c in allowed])

class SchemaEditor:
    """ a simple TTW editor for Archetypes schemas """

    security = ClassSecurityInfo()

    security.declareProtected(ManageSchema, 'atse_init')
    def atse_init(self, schema, filtered_schemas=('default', 'metadata')):
        self._ms = ManagedSchema(schema.fields())
        self._filtered_schemas = filtered_schemas

    security.declareProtected(View, 'atse_getSchema')
    def atse_getSchema(self):
        """ return the concatenation of all schemas """       
        return self._ms

    security.declareProtected(View, 'atse_getSchemataNames')
    def atse_getSchemataNames(self):
        """ return names of all schematas """
        if not hasattr(self, '_filtered_schemas'):          # migration
            self._filtered_schemas = ('default', 'metadata')
        return [n  for n in self._ms.getSchemataNames() if not n in self._filtered_schemas]

    security.declareProtected(View, 'atse_getSchemata')
    def atse_getSchemata(self, name):
        """ return a schemata given by its name """
        s = ManagedSchema()
        for f in self._ms.getSchemataFields(name):
            s.addField(f)
        return ImplicitAcquisitionWrapper(s, self)

    ######################################################################
    # Add/remove schematas
    ######################################################################

    security.declareProtected(ManageSchema, 'atse_addSchemata')
    def atse_addSchemata(self, name, RESPONSE=None):
        """ add a new schemata """
        if not name:
            raise TypeError(self.Translate('atse_empty_name', 'Empty ID given'))

        if name in self._ms.getSchemataNames():
            raise ValueError(self.Translate('atse_exists', 
                             'Schemata "$schemata" already exists', schemata=name))
        if not id_regex.match(name):
            raise ValueError(self.Translate('atse_invalid_id_for_schemata', 
                             '"$schemata" is an invalid ID for a schemata', schemata=name))

        self._ms.addSchemata(name)
        self._p_changed = 1

        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.Translate('atse_added', 'Schemata added'), schemata=name)

    security.declareProtected(ManageSchema, 'atse_delSchemata')
    def atse_delSchemata(self, name, RESPONSE=None):
        """ delete a schemata """

        if len(self._ms.getSchemataNames()) == 2: # default is hidden
            raise RuntimeError(self.Translate('atse_can_not_remove_last_schema', 'Can not remove the last schema'))
        self._ms.delSchemata(name)
        self._p_changed = 1
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.Translate('atse_deleted', 'Schemata deleted'), schemata=self._ms.getSchemataNames()[0])

    ######################################################################
    # Field manipulation
    ######################################################################

    security.declareProtected(ManageSchema, 'atse_delField')
    def atse_delField(self, name, RESPONSE=None):
        """ remove a field from a schemata"""

        if name in UNDELETEABLE_FIELDS:
            raise ValueError(self.Translate('atse_field_not_deleteable',
                                            'field "$name" can not be deleted because it is protected from deletion',   
                                            name=name))

        old_schemata = self._ms[name].schemata
        self._ms.delField(name)    

        if old_schemata in self._ms.getSchemataNames():
            return_schemata = old_schemata
        else:
            return_schemata = self._ms.getSchemataNames()[0]
	
        self._p_changed = 1
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.Translate('atse_field_deleted', 'Field deleted'), schemata=return_schemata)


    security.declareProtected(ManageSchema, 'atse_update')
    def atse_update(self, fielddata,  REQUEST, RESPONSE=None):
        """ update a single field"""

        R = REQUEST.form
        FD = fielddata

        ## ATT: this should go into a dedicated method
        if R.has_key('add_field'):
            if not R['name']:
                raise ValueError(self.Translate('atse_empty_field_name', 
                                 'Field name is empty'))

            if not id_regex.match(R['name']):
                raise ValueError(self.Translate('atse_not_a_valid_id', 
                                 '"$id" is not a valid ID', id=R['name']))

            if R['name'] in [f.getName() for f in self._ms.fields()]:
                raise ValueError(self.Translate('atse_field_already_exists', 
                                 '"$id" exists already', id=R['name']))

            fieldset = FD.schemata    
            field = StringField(R['name'], schemata=fieldset, widget=StringWidget)
            self._ms.addField(field)
            self._p_changed = 1
            util.redirect(RESPONSE, 'pcng_schema_editor', 
                          self.Translate('atse_field_added', 'Field added'), schemata=fieldset, field=R['name'])
            return            

        if   FD.type == 'StringField':     field = StringField
        elif FD.type == 'IntegerField':    field = IntegerField
        elif FD.type == 'FloatField':      field = FloatField
        elif FD.type == 'FixedPointField': field = FixedPointField
        elif FD.type == 'BooleanField':    field = BooleanField
        elif FD.type == 'LinesField':      field = LinesField
        elif FD.type == 'DateTimeField':   field = DateTimeField
        else: raise TypeError(self.Translate('atse_unknown_field', 'unknown field type: $field', field=FD.field))

        D = {}    # dict to be passed to the field constructor
        D['default'] = FD.get('default', '')
        D['schemata'] = FD.schemata
        D['createindex'] = FD.get('createindex', 0)
         
        # build widget
        if   FD.widget == 'String':      widget = StringWidget()
        elif FD.widget == 'Select':      widget = SelectionWidget(format='select')
        elif FD.widget == 'Flex':        widget = SelectionWidget(format='flex')
        elif FD.widget == 'Radio':       widget = SelectionWidget(format='radio')
        elif FD.widget == 'Textarea':    widget = TextAreaWidget()
        elif FD.widget == 'Calendar':    widget = CalendarWidget()
        elif FD.widget == 'Boolean':     widget = BooleanWidget()
        elif FD.widget == 'MultiSelect': widget = MultiSelectionWidget()
        elif FD.widget == 'Keywords':    widget = KeywordWidget()
        elif FD.widget == 'Richtext':    widget = RichWidget()
        elif FD.widget == 'Password':    widget = PasswordWidget()
        elif FD.widget == 'Lines':       widget = LinesWidget()
        elif FD.widget == 'Visual':      widget = VisualWidget()
        elif FD.widget == 'Epoz':        widget = EpozWidget()
        elif FD.widget == 'Image':       widget = ImageWidget()
        elif FD.widget == 'Integer':     widget = IntegerWidget()
        elif FD.widget == 'Decimal':     widget = DecimalWidget()
        elif FD.widget == 'Reference':   widget = ReferenceWidget()
        elif FD.widget == 'Picklist':    widget = PicklistWidget()
        elif FD.widget == 'InAndOut':    widget = InAndOutWidget()
        else: raise ValueError(self.Translate('atse_unknown_widget', 'unknown widget type: $widget', widget=d.widget))

        if FD.has_key('widgetsize'):
            widget.size = FD.widgetsize
            widget.rows = 5
            widget.cols = 60
        
        elif FD.has_key('widgetcols') and FD.has_key('widgetrows'):
            widget.rows = FD['widgetrows']
            widget.cols = FD['widgetcols']
            widget.size = 60
        else:
            raise RuntimeError

        widget.visible = 1
        widget.label = FD.label
        widget.label_msgid = 'label_' + FD.label
        widget.i18n_domain = 'plonecollectorng'

        D['widget'] = widget

        # build DisplayList instance for SelectionWidgets
        if FD.widget in ('Radio', 'Select', 'MultiSelect', 'Flex', 'Picklist',
                         'InAndOut'):
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
                    if line.find('|') == -1:
                        k = v = line
                    else:
                        k,v = line.split('|', 1)

                    k = remove_unallowed_chars(k)
                    l.append( (k,v))

                D['vocabulary'] = DisplayList(l)

        D['required'] = FD.get('required', 0)

        newfield = field(FD.name, **D)
        self._ms.replaceField(FD.name, newfield)
        self._p_changed = 1
        self._ms._p_changed = 1

        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.Translate('atse_field_changed', 'Field changed'), 
                      schemata=FD.schemata, field=FD.name)

    ######################################################################
    # Moving schematas and fields
    ######################################################################

    security.declareProtected(ManageSchema, 'atse_schemataMoveLeft')
    def atse_schemataMoveLeft(self, name, RESPONSE=None):
        """ move a schemata to the left"""
        self._ms.moveSchemata(name, -1)
        self._p_changed = 1
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.Translate('atse_moved_left', 'Schemata moved to left'), schemata=name)

    security.declareProtected(ManageSchema, 'atse_schemataMoveRight')
    def atse_schemataMoveRight(self, name, RESPONSE=None):
        """ move a schemata to the right"""
        self._ms.moveSchemata(name, 1)
        self._p_changed = 1
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.Translate('atse_moved_right', 'Schemata moved to right'), schemata=name)

    security.declareProtected(ManageSchema, 'atse_fieldMoveLeft')
    def atse_fieldMoveLeft(self, name, RESPONSE=None):
        """ move a field of schemata to the left"""
        self._ms.moveField(name, -1)
        self._p_changed = 1
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.Translate('atse_field_moved_up', 'Field moved up'), schemata=self._ms[name].schemata, field=name)

    security.declareProtected(ManageSchema, 'atse_fieldMoveRight')
    def atse_fieldMoveRight(self, name, RESPONSE=None):
        """ move a field of schemata down to the right"""
        self._ms.moveField(name, 1)
        self._p_changed = 1
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.Translate('atse_field_moved_down', 'Field moved down'), schemata=self._ms[name].schemata, field=name)

    security.declareProtected(ManageSchema, 'atse_changeSchemataForField')
    def atse_changeSchemataForField(self, name, schemata_name, RESPONSE=None):
        """ move a field from the current fieldset to another one """
        self._ms.changeSchemataForField(name, schemata_name)
        self._p_changed = 1
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.Translate('atse_field_moved', 'Field moved to other fieldset'), schemata=schemata_name, field=name)


    ######################################################################
    # Hook for UI
    ######################################################################

    security.declareProtected(ManageSchema, 'atse_getField')
    def atse_getField(self, name):
        """ return a field by its name """
        return self._ms[name]

    security.declareProtected(ManageSchema, 'atse_getFieldType')
    def atse_getFieldType(self, field):
        """ return the type of a field """
        return field.__class__.__name__
    
    security.declareProtected(ManageSchema, 'atse_formatVocabulary')
    def atse_formatVocabulary(self, field):
        """ format the DisplayList of a field to be display
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

    def _dump_schema(self):
        """ only for debugging """
        for schemata in self._ms.getSchemataNames():
            print '%s: %s' % (schemata, ', '.join([f.getName() for f in  self._ms.getSchemataFields(schemata)]))

    security.declareProtected(ManageSchema, 'migrate_schema')
    def migrate_schema(self):
        """ migrate to ManagedSchema """

        old_schema = self._ms.copy()
        self._ms = ManagedSchema()
        for schemata_name in old_schema.getSchemataNames():
            for field in old_schema.getSchemataFields(schemata_name):
                try:
                    field._validationLayer()  # re-init validation layer (ValidationChain etc)
                except AttributeError:
                    pass
                self._ms.addField(field)
        self._p_changed = 1

    security.declareProtected(ManageSchema, 'atse_schema_baseclass')
    def atse_schema_baseclass(self):
        """ return name of baseclass """
        return str(self._ms.__class__)

    security.declareProtected(ManageSchema, 'atse_migrate_vocabularies')
    def atse_migrate_vocabularies(self):
        """ Convert DisplayList instance to new AT standard where keys *must*
            be StringType and not UnicodeType.
        """

        for field in self._ms.fields():
            if hasattr(field, 'vocabulary'):
                if field.vocabulary.__class__.__name__ == 'DisplayList':
                    D = DisplayList()
                    for k in field.vocabulary.keys():
                        if isinstance(k, unicode):
                            k = k.encode('iso-8859-15', 'ignore')
                        v = field.vocabulary.getValue(k)
                        D.add(k,v)
                    field.vocabulary = D

        return 'Conversion done'

InitializeClass(SchemaEditor)
