from Products.PortalTransforms.interfaces import itransform
import re

class URLToHyperlink:
    """transform which replaces urls and email into hyperlinks"""

    __implements__ = itransform

    __name__ = "url_to_hyperlink"
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
        urlchars = r'[A-Za-z0-9/:@_%~#=&\.\-\?]+'
        url = r'["=]?((http|ftp|https):%s)' % urlchars
        emailRegexp = r'["=]?(\b\S+@\S+\b)'
        # These aren't tested yet
        #emailRegexp = r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}'
        #emailRegexp = r'^[a-z0-9]+([_|-|.][a-z0-9]+)*\@([a-z0-9]+((-*)(.*)[a-z0-9]+)*\.(com|edu|biz|org|gov|int|info|mil|net|arpa|name|museum|coop|aero|[a-z][a-z])|(\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\]))$'
        
        regexp = re.compile(url, re.I|re.S)
        def replaceURL(match):
            url = match.groups()[0]
            return '<a href="%s">%s</a>' % (url, url)
        text = regexp.subn(replaceURL, orig)[0]
        
        regexp = re.compile(emailRegexp, re.I|re.S)
        def replaceEmail(match):
            url = match.groups()[0]
            return '<a href="mailto:%s">%s</a>' % (url, url)
        text = regexp.subn(replaceEmail, text)[0]
    
        data.setData(text)
        return data

def register():
    return URLToHyperlink()
