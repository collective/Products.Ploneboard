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
        self.urlRegexp = re.compile(r'((?:ftp|https?)://(?:[a-z0-9](?:[-a-z0-9]*[a-z0-9])?\.)+(?:com|edu|biz|org|gov|int|info|mil|net|name|museum|coop|aero|[a-z][a-z])\b(?:\d+)?(?:\/[^;"\'<>()\[\]{}\s\x7f-\xff]*(?:[.,?]+[^;"\'<>()\[\]{}\s\x7f-\xff]+)*)?)', re.I|re.S|re.U)
        self.emailRegexp = re.compile(r'["=]?(\b[A-Z0-9._%-]+@[A-Z0-9._%-]+\.[A-Z]{2,4}\b)', re.I|re.S|re.U)
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
        text = orig
        if not isinstance(text, unicode):
            text = unicode(text, 'utf-8', 'replace')
        
        # Replace hyperlinks with clickable <a> tags
        def replaceURL(match):
            url = match.groups()[0]
            return '<a href="%s">%s</a>' % (url, url)
        text = self.urlRegexp.subn(replaceURL, text)[0]
        
        # Replace email strings with mailto: links
        def replaceEmail(match):
            url = match.groups()[0]
            return '<a href="mailto:%s">%s</a>' % (url, url)
        text = self.emailRegexp.subn(replaceEmail, text)[0]
    
        data.setData(text.encode('utf-8'))
        return data

def register():
    return URLToHyperlink()
