#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2004 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA 
#
"""

$Id: schemata.py,v 1.29 2004/05/30 14:51:16 godchap Exp $
""" 
__author__  = ''
__docformat__ = 'restructuredtext'

from copy import deepcopy

from Products.Archetypes.public import *
#from Products.Archetypes.TemplateMixin import TemplateMixinSchema
from Products.Archetypes.Marshall import RFC822Marshaller, PrimaryFieldMarshaller
from DateTime import DateTime
from Products.CMFCore import CMFCorePermissions
from Products.ATContentTypes import Validators
from Products.ATContentTypes.config import *

from Products.validation.validators.SupplValidators import MaxSizeValidator

try:
    True
except NameError:
    True=1
    False=0

if HAS_EXT_STORAGE:
    from Products.ExternalStorage.ExternalStorage import ExternalStorage
else:
    # dummy storage
    from Products.Archetypes.Storage import Storage as BaseStorage

    class ExternalStorage(BaseStorage):
        def __init__(self, prefix='', archive=False):
            pass


ATContentTypeBaseSchema = BaseSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(description = "Enter a brief description", 
                                      description_msgid = "help_description",
                                      label = "Description",
                                      label_msgid = "label_description",
                                      rows = 5,
                                      i18n_domain = "plone")),
    ))
    
ATContentTypeSchema = ATContentTypeBaseSchema + Schema((    
    # TemplateMixin
    StringField('layout',
                accessor="getLayout",
                mutator="setLayout",
                write_permission=TEMPLATE_MIXIN_PERMISSION,
                default_method="getDefaultLayout",
                vocabulary="_voc_templates",
                #enforceVocabulary=1,
                widget=SelectionWidget(description="Choose a template that will be used for viewing this item.",
                                       description_msgid = "help_template_mixin",
                                       label = "View template",
                                       label_msgid = "label_template_mixin",
                                       i18n_domain = "plone",
                                       visible={'view' : 'hidden',
                                                'edit' : ENABLE_TEMPLATE_MIXIN and 'visible' or 'hidden'},
                                       )),
    ))
    

###
# AT Content Type Document
###
ATDocumentSchema = ATContentTypeSchema + Schema((
    TextField('text',
              required = 1,
              searchable = 1,
              primary = 1,
              validators = ('isTidyHtmlWithCleanup',),
              #validators = ('isTidyHtml',),
              default_content_type = 'text/restructured',
              default_output_type = 'text/html',
              allowable_content_types = ('text/structured',
                                         'text/restructured',
                                         'text/html',
                                         'text/plain',
                                         'text/plain-pre',
                                         'text/python-source',),
              widget = RichWidget(description = "The body text of the document.",
                                  description_msgid = "help_body_text",
                                  label = "Body text",
                                  label_msgid = "label_body_text",
                                  rows = 25,
                                  i18n_domain = "plone")),
    ), marshall=RFC822Marshaller()
    )

###
# AT Content Type Event
###
ATEventSchema = ATContentTypeSchema + Schema((
    StringField('location',
                searchable = 1,
                widget = StringWidget(description = "Enter the location where the event will take place.",
                                      description_msgid = "help_event_location",
                                      label = "Event Location",
                                      label_msgid = "label_event_location",
                                      i18n_domain = "plone")),
    
    LinesField('eventType',
               required = 1,
               searchable = 1,
               vocabulary = 'getEventTypes',
               languageIndependent=True,
               widget = MultiSelectionWidget(size = 6,
                                             description = "Select the type of event. Multiple event types possible.",
                                             description_msgid = "help_event_type",
                                             label = "Event Type",
                                             label_msgid = "label_event_type",
                                             i18n_domain = "plone")),

    StringField('eventUrl',
                required=0,
                searchable = 1,
                accessor='event_url',
                validators = ('isURL',),
                widget = StringWidget(description = "Enter the optional web address of a page containing more info about the event. ",
                                      description_msgid = "help_url",
                                      label = "Event URL",
                                      label_msgid = "label_url",
                                      i18n_domain = "plone")),
    DateTimeField('startDate',
                  required = 1,
                  searchable = 1,
                  accessor='start',
                  default=DateTime(),
                  languageIndependent=True,
                  widget = CalendarWidget(description="Enter the starting date and time, or click the calendar icon and select it. ",
                                          description_msgid = "help_event_start",
                                          label="Event Starts",
                                          label_msgid = "label_event_start",
                                          i18n_domain = "plone")),

    DateTimeField('endDate',
                  required = 1,
                  searchable = 1,
                  accessor='end',
                  default=DateTime(),
                  languageIndependent=True,
                  widget = CalendarWidget(description= "Enter the ending date and time, or click the calendar icon and select it. ",
                                          description_msgid = "help_event_end",
                                          label = "Event Ends",
                                          label_msgid = "label_event_end",
                                          i18n_domain = "plone")),
    StringField('contactName',
                required=0,
                searchable = 1,
                accessor='contact_name',
                widget = StringWidget(description = "Enter a contact person or organization for the event.",
                                      description_msgid = "help_contact_name",
                                      label = "Contact Name",
                                      label_msgid = "label_contact_name",
                                      i18n_domain = "plone")),
    StringField('contactEmail',
                required=0,
                searchable = 1,
                accessor='contact_email',
                validators = ('isEmail',),
                widget = StringWidget(description = "Enter an e-mail address to use for information regarding the event.",
                                      description_msgid = "help_contact_email",
                                      label = "Contact E-mail",
                                      label_msgid = "label_contact_email",
                                      i18n_domain = "plone")),
    StringField('contactPhone',
                required=0,
                searchable = 1,
                accessor='contact_phone',
                validators = ('isInternationalPhoneNumber',),
                widget = StringWidget(description = "Enter the phone number to call for information and/or booking.",
                                      description_msgid = "help_contact_phone",
                                      label = "Contact Phone",
                                      label_msgid = "label_contact_phone",
                                      i18n_domain = "plone")),
    ), marshall = RFC822Marshaller())

###
# AT Content Type Favorite
###
ATFavoriteSchema = ATContentTypeSchema + Schema((
    StringField('remoteUrl',
                required = 1,
                searchable = 1,
                accessor='_getRemoteUrl',
                primary=1,
                validators = (),
                widget = StringWidget(description="The address of the location. Prefix is optional; if not provided, the link will be relative.",
                                      description_msgid = "help_url",
                                      label = "URL",
                                      label_msgid = "label_url",
                                      i18n_domain = "plone")),
    ))

###
# AT Content Type File
###

ATFileSchema = ATContentTypeSchema + Schema((
    FileField('file',
              required = 1,
              primary=1,
              validators = MaxSizeValidator('checkFileMaxSize', maxsize=MAX_FILE_SIZE),
              widget = FileWidget(description = "Select the file to be added by clicking the 'Browse' button.",
                                  description_msgid = "help_file",
                                  label= "File",
                                  label_msgid = "label_file",
                                  i18n_domain = "plone"))

    ), marshall=PrimaryFieldMarshaller())

ATExtFileSchema = ATContentTypeSchema + Schema((
    FileField('file',
              required = 1,
              primary=1,
              validators = MaxSizeValidator('checkFileMaxSize', maxsize=MAX_FILE_SIZE),
              storage=ExternalStorage(prefix='atct', archive=False),
              widget = FileWidget(description = "Select the file to be added by clicking the 'Browse' button.",
                                  description_msgid = "help_file",
                                  label= "File",
                                  label_msgid = "label_file",
                                  i18n_domain = "plone"))
    ), marshall=PrimaryFieldMarshaller())

###
# AT Content Type Folder
###
ATFolderSchema = OrderedBaseFolder.schema + ATContentTypeSchema

ATBTreeFolderSchema = BaseBTreeFolder.schema + ATContentTypeSchema

###
# AT Content Type Image
###
ATImageSchema = ATContentTypeSchema + Schema((
    ImageField('image',
               required = 1,
               primary=1,
               sizes= {'preview' : (400, 400),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                       'listing' :  (16, 16),
                      },
               validators = MaxSizeValidator('checkFileMaxSize', maxsize=MAX_IMAGE_SIZE),
               widget = ImageWidget(description = "Select the image to be added by clicking the 'Browse' button.",
                                    description_msgid = "help_image",
                                    label= "Image",
                                    label_msgid = "label_image",
                                    i18n_domain = "plone"))
    ), marshall=PrimaryFieldMarshaller())

ATExtImageSchema = ATContentTypeSchema + Schema((
    ImageField('image',
               required = 1,
               primary=1,
               storage=ExternalStorage(prefix='atct', archive=False),
               sizes= {'preview' : (400, 400),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                       'listing' :  (16, 16),
                      },
               validators = MaxSizeValidator('checkFileMaxSize', maxsize=MAX_IMAGE_SIZE),
               widget = ImageWidget(description = "Select the image to be added by clicking the 'Browse' button.",
                                    description_msgid = "help_image",
                                    label= "Image",
                                    label_msgid = "label_image",
                                    i18n_domain = "plone"))
    ), marshall=PrimaryFieldMarshaller())


###
# AT Content Type Link
###
ATLinkSchema = ATContentTypeSchema + Schema((
    StringField('remoteUrl',
                required = 1,
                searchable = 1,
                primary=1,
                validators = ('isURL',),
                widget = StringWidget(description="The address of the location. Prefix is optional; if not provided, the link will be relative.",
                                      description_msgid = "help_url",
                                      label = "URL",
                                      label_msgid = "label_url",
                                      i18n_domain = "plone")),
    ))

###
# AT Content Type News Item
###
ATNewsItemSchema = ATContentTypeSchema + Schema((
    TextField('text',
              required = 1,
              searchable = 1,
              primary = 1,
              validators = ('isTidyHtmlWithCleanup',),
              #validators = ('isTidyHtml',),
              default_content_type = 'text/restructured',
              default_output_type = 'text/html',
              allowable_content_types = ('text/structured',
                                         'text/restructured',
                                         'text/html',
                                         'text/plain',
                                         ),
              widget = RichWidget(description = "The body text of the document.",
                                  description_msgid = "help_body_text",
                                  label = "Body text",
                                  label_msgid = "label_body_text",
                                  rows = 25,
                                  i18n_domain = "plone")),
    #StringField('newstype',
    #            vocabulary=NEWS_TYPES,
    #           widget=SelectionWidget(label='Type of News',
    #                                   description='The type of news item.',
    #                                   label_msgid='label_newstype',
    #                                   description_msgid='help_newstype',
    #                                   i18n_domain='plone'),
    #            ),
    ), marshall=RFC822Marshaller()
    )

###
# AT Content Type Topic
###
ATTopicSchema = BaseFolder.schema + ATContentTypeSchema + Schema((
    BooleanField('acquireCriteria',
                required=0,
                mode="rw",
                default=0,
                widget=BooleanWidget(
                                label="Inherit Criteria",
                                label_msgid="label_inherit_criteria",
                                description="Toggles inheritance of criteria. For example, if you " \
                                             "have specified that only items from the last three days " \
                                             "should be shown in a Topic above the current one, this " \
                                             "Topic will also have that criterion automatically.",
                                description_msgid="help_inherit_criteria",
                                i18n_domain = "plone"),
                ),
    ))
