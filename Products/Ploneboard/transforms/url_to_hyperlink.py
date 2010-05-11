import re
from zope.interface import implements
from Products.PortalTransforms.interfaces import itransform
try:
    from Products.PortalTransforms.interfaces import ITransform
except ImportError:
    ITransform = None

hider = "##HIDE"
schemematcher = re.compile ("(mailto|telnet|gopher|http|https|ftp)", re.I)
hiddenschemematcher = re.compile ("(mailto|telnet|gopher|http|https|ftp)" + hider, re.I)
elementmatcher = re.compile("<[^>]+>")
emailRegexp = re.compile(r'["=]?(\b[A-Z0-9._%+=?\*^-]+@[A-Z0-9._%-]+\.[A-Z]{2,4}\b)', re.I|re.S|re.U)
urlmatcher = re.compile(
                    r"\b(?P<url>(?P<scheme>http|https|ftp|telnet|mailto|gopher):(?P<interfix>//)"
                    r"(?:(?P<login>(?P<username>[a-zA-Z0-9]+)(?::(?P<password>[A-Za-z0-9]+))?)@)?"
                    r"(?P<hostname>[A-Za-z0-9.-]+(?::(?P<port>[0-9]+))?)"
                    r"(?P<path>[A-Za-z0-9@~_=?/.&;%#+-]*))", re.I)

class URLToHyperlink:
    """transform which replaces urls and email into hyperlinks"""

    __implements__ = itransform

    if ITransform:
        implements(ITransform) 

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

    def linkify(input):
        def hidescheme(match):
            text=input[match.start():match.end()]
            text=text.replace("@", "@"+hider)
            return schemematcher.sub("\\1"+hider, text)

        def replaceEmail(match):
            url = match.groups()[0]
            return '<a href="mailto:%s">%s</a>' % (url, url)

        buf=elementmatcher.sub(hidescheme, input)
        buf=urlmatcher.sub(r'<a href="\1">\1</a>', buf)
        buf=emailRegexp.subn(replaceEmail, buf)[0]
        buf=buf.replace(hider, "")
        return buf
    linkify=staticmethod(linkify)

    def convert(self, orig, data, **kwargs):
        text = orig
        if not isinstance(text, unicode):
            text = unicode(text, 'utf-8', 'replace')
        
        text = self.linkify(text)
    
        data.setData(text.encode('utf-8'))
        return data

def register():
    return URLToHyperlink()

__all__ = [ "URLToHyperlink", "register" ]
