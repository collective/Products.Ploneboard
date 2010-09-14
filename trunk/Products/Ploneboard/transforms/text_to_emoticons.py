import copy
import re

from ZODB.PersistentMapping import PersistentMapping
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Ploneboard.utils import TransformDataProvider
from Products.PortalTransforms.interfaces import itransform
try:
    from Products.PortalTransforms.interfaces import ITransform
except ImportError:
    ITransform = None

class EmoticonDataProvider(TransformDataProvider):
    def __init__(self):
        """ We need to redefine config and config_metadata
        in base class.
        """
        self.config = PersistentMapping()
        self.config_metadata = PersistentMapping()
        
        self.config.update({ 'inputs' : self.defaultEmoticons()})

        self.config_metadata.update({
            'inputs' : {
                'key_label' : 'emoticon code', 
                'value_label' : 'image name', 
                'description' : 'Emoticons to images mapping'}
            })

    def defaultEmoticons():
        emoticons = { ':)' : '<img src="smiley_smile.png" alt=":)" title="Smile" />'
                    , ':(' : '<img src="smiley_sad.png" alt=":(" title="Sad" />'
                    , '8-)' : '<img src="smiley_cool.png" alt="8)" title="Cool" />'
                    , ':D' : '<img src="smiley_lol.png" alt=":D" title="Big grin" />'
                    , ':|' : '<img src="smiley_skeptic.png" alt=":|" title="Skeptic" />'
                    , ':o' : '<img src="smiley_surprised.png" alt=":o" title="Surprised" />'
                    , ':P' : '<img src="smiley_tongue.png" alt=":P" title="Tongue-in-cheek" />'
                    , ';)' : '<img src="smiley_wink.png" alt=";)" title="Wink" />'
                    , ':-)' : '<img src="smiley_smile.png" alt=":)" title="Smile" />'
                    , ':-(' : '<img src="smiley_sad.png" alt=":(" title="Sad" />'
                    , ':-D' : '<img src="smiley_lol.png" alt=":D" title="Big grin" />'
                    , ':-|' : '<img src="smiley_skeptic.png" alt=":|" title="Skeptic" />'
                    , ':-o' : '<img src="smiley_surprised.png" alt=":o" title="Surprised" />'
                    , ':-P' : '<img src="smiley_tongue.png" alt=":P" title="Tongue-in-cheek" />'
                    , ';-)' : '<img src="smiley_wink.png" alt=";)" title="Wink" />'
                    }
        return emoticons
    defaultEmoticons=staticmethod(defaultEmoticons)

def registerDataProvider():
    return EmoticonDataProvider()


class TextToEmoticons:
    """transform which replaces text emoticons into urls to emoticons images"""

    __implements__ = itransform
    if ITransform:
        implements(ITransform) 

    __name__ = "text_to_emoticons"
    output = "text/plain"

    def __init__(self, name=None, inputs=('text/plain',)):
        self.config = { 'inputs' : inputs, }
        self.config_metadata = {
            'inputs' : ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            }
        if name:
            self.__name__ = name
            
    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        """ Replace in 'orig' all occurences of any key in the given
          dictionary by its corresponding value.  Returns the new string.
        """
        # Get acquisition context
        context = kwargs.get('context')
        
        url_tool = getToolByName(context, 'portal_url')
        dict = EmoticonDataProvider.defaultEmoticons()
        
        # Here we need to find relative images path to the root of site
        # This is done for image cashing.
        dictionary = copy.deepcopy(dict)
        
        rev_dict = {}
        for k, v in dict.items():
            rev_dict[v] = k
        obj_ids = tuple(dict.values())
        # To speed up search we are narrowing search path
        start_path = url_tool.getPortalPath() + '/portal_skins'
        start_obj = context.restrictedTraverse(start_path + '/custom')
        results = context.PrincipiaFind(start_obj, obj_ids=obj_ids, obj_metatypes=('Image', ), search_sub=1)
        start_obj = context.restrictedTraverse(start_path + '/ploneboard_templates')
        results.extend(context.PrincipiaFind(start_obj, obj_ids=obj_ids, obj_metatypes=('Image', ), search_sub=1))
        for rec in results:
            obj = rec[1]
            dictionary[rev_dict[obj.getId()]] = '<img src="%s" />' % url_tool.getRelativeContentURL(obj)
        
        #based on ASPN recipe - http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81330
        # Create a regular expression  from the dictionary keys
        regex = re.compile("(%s)(?!\")" % "|".join(map(re.escape, dictionary.keys())))
        # For each match, look-up corresponding value in dictionary
        newdata = regex.sub(lambda mo, d=dictionary: d[mo.string[mo.start():mo.end()]], orig) 
        data.setData(newdata)
        return data

def register():
    return TextToEmoticons()
