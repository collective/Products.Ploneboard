from Products.Archetypes.public import *
from Products.CompositePack.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName

class Titles(BaseContentMixin):

    meta_type = portal_type = 'CompositePack Titles'
    archetype_name = 'Navigation Titles'
    global_allow = 0
    
    schema = MinimalSchema + Schema((
        StringField(
        'description',
        widget=StringWidget(label='Description',
                            description=('Description used as a subtitle.'))
        ),
        ))

    factory_type_information={
        'content_icon':'composite.gif',
        }

    actions=  (
           {'action':      '''string:$object_url/back_to_composite''',
            'category':    '''object''',
            'id':          'view',
            'name':        'view',
            'permissions': ('''View''',)},

           ) 

registerType(Titles, PROJECTNAME)
