from Products.PortalTransforms.interfaces import itransform
from ZODB.PersistentMapping import PersistentMapping
import re

class EmoticonService:
    def __init__(self):
        self.emap = PersistentMapping()
        self.emap.update({':)' : "<img src='smile.png'>", ':(' : "<img src='sad.png'>"})
        
    def getEmoticon(self, text):
        """Returns url"""
        return self.emap.get(text)
    
    def getEmoticonsMapping(self):
        """Returns mapping of text to url """
        return self.emap
        
    def setEmoticonMapping(self, text, url):
        self.emap.update({text : url})

class TextToEmoticons:
    """transform which replaces text emoticons into urls to emoticons images"""

    __implements__ = itransform

    __name__ = "text_to_emoticons"
    output = "text/html"

    def __init__(self, name=None, inputs=('text/html',)):
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
        """ Replace in 'text' all occurences of any key in the given
          dictionary by its corresponding value.  Returns the new string.
        """
        dictionary = EmoticonService().getEmoticonsMapping()
        #based on ASPN recipe - http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81330
        # Create a regular expression  from the dictionary keys
        regex = re.compile("(%s)" % "|".join(map(re.escape, dictionary.keys())))
        # For each match, look-up corresponding value in dictionary
        newdata = regex.sub(lambda mo, d=dictionary: d[mo.string[mo.start():mo.end()]], orig) 
        data.setData(newdata)
        return data

def register():
    return TextToEmoticons()
