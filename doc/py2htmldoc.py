#!/usr/local/bin/python -O

""" 
    Automatic Python Documentation in HTML

    This tool will parse all files in a given directory and build an
    internal object structure closely resembling the code structure
    found in the files.

    Using this internal representation, the obejcts are then called
    to produce a readable output -- currently only HTML is supported.

    This module should probably make use of the standard module
    parser, I but didn't have the time back when I originally wrote
    this, to learn all about Pythons grammar and ast-trees. The
    regexp's I used work nice for most situations, though dynamically
    defined code (like code in if...else...-clauses) is not parsed.

    The doc-strings are processed by the doc_string-class and may
    contain special character sequences to enhance the output. Look
    at the as_HTML-method of that class to find out more about
    it's features.

    Caveats:

    - it will only work for doc-strings enclosed in triple double-quotes
      that appear /balanced/ in the source code (use \"\"\" if you have to
      include single occurences)
    - since the doc-strings are written more or less directly into
      the HTML-file you have to be careful about using <, > and &
      in them, since these could lead to unwanted results, e.g.
      like in 'if a<c then: print a>b'; writing 'if a < c then: print a > b'
      causes no problem; _note:_ this is a feature so you can use
      normal HTML-tags in your doc-strings; use the #-trick explained
      in the doc_string-class instead !
      [Maybe I should reverse this feature: make normal text the default
       and HTML the exception that needs escaping -- don't use any HTML
       in my current doc-strings anyway]
    - code could be made faster by using string.join and %s... oh well.
    - doc string highlighting isn't done nicely (but works fine for my code :-)
    - tuples in function/method declarations can get this little tool
      pretty confused...
    - this code is full of circular references; but then,
      I normally only use it as script -- not as module to other programs

    Notes:

    - you might want to take a look at gendoc and HTMLgen for doing
      a more elaborate job (see: www.python.org for more infos)
    - to get colorized HTML versions of yyour Python scripts have a look
      at py2html.py (downloadable from my Python pages on starship)

    History:

    - 0.5: minor fixes to the regexps (thanks to Tim Peters)
    - 0.6: fixed a buglet in rx_bodyindent[2] that sneaked
           in from 0.4 to 0.5 (thanks to Dinu Gherman) and
           added a few more /human/ formats :-)
    - 0.7: changed the parts-regexp to not break code at comments
           (this sometimes cut off some methods from classes)
    - 0.8: fixed bug that cut away first character from bullets;
           added __version__ parsing and source code highlighting
           provisions
    - 0.9: Added a fix to support spaces between class/function/method
           names and the parameter list (courtesy of Keith Davidson);
           added 'o' as list item
    - 0.9.1: Added sorting of methods, classes,
             functions; added special parameter formatting: an empty line
             truncates the remaining parameters from the docs

    The latest version is always available from my Python pages:

           http://starship.python.net/~lemburg/

    
    
-----------------------------------------------------------------------------
(c) Copyright by Marc-Andre Lemburg (mailto:mal@lemburg.com)

    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee or royalty is hereby granted,
    provided that the above copyright notice appear in all copies and that
    both that copyright notice and this permission notice appear in
    supporting documentation or portions thereof, including modifications,
    that you make.

    THE AUTHOR MARC-ANDRE LEMBURG DISCLAIMS ALL WARRANTIES WITH REGARD TO
    THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
    FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
    INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
    FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
    NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
    WITH THE USE OR PERFORMANCE OF THIS SOFTWARE !

"""

__version__  = '0.9.1'
__package_info__ = """
BEGIN PYTHON-PACKAGE-INFO 1.0
Title:                  Automatic Python Documentation in HTML
Current-Version:        0.9.1
Home-Page:              http://starship.python.net/~lemburg
Primary-Site:           http://starship.python.net/~lemburg/doc.py

This tool will parse all files in a given directory and build an
internal object structure closely resembling the code structure
found in the files.

Using this internal representation, the objects are then called
to produce a readable output -- currently only HTML is supported.
END PYTHON-PACKAGE-INFO
"""

import sys,os,regex,string,regsub,time

# list markers
list_markers = '\*+-·o'

# reg. expressions used
rx_class = regex.compile('\( *\)class +\([^:( ]+\) *\((\([^)]*\))\)? *:')
rx_function = regex.compile('\( *\)def +\([^( ]+\) *'
                            '(\(\([^()]\|([^)]*)\)*\)) *:')
rx_method = rx_function
rx_bodyindent = regex.compile('^\( *\)[^ \n]')
rx_bodyindent_2 = regex.compile('\( *\)[^ \n]')
rx_version = regex.compile(' *__version__ *= *[\'\"]\([^\'\"]+\)[\'\"]')
# cache some common parts regexps
rx_parts = {}
for indent in range(0,17,4):
    si = indent * ' '
    rs = '^'+si+'def \|^'+si+'class \|^'+si+'\"\"\"\|^'+ \
         si+'import \|^'+si+'from \|^'+si+'__version__'#\|^'+si+'[^ \n]'
    rx = regex.compile(rs)
    rx_parts[indent] = rx

# used tabsize
tabsize = 8

# some gobal options
hrefprefix = '' # put infront of all external HTML-links... helps when
                # putting the pages onto some website.
#highlighted = 'http://starship.python.net/~lemburg/py2html.cgi/%s'
                # URL of the source code highlighting mediator to be used;
                # %s will be replaced by the hrefprefix+filename
highlighted = '%s.html' 
                # If want to use static versions created with py2html.py,
                # use this version

# Errors
ParseError = 'ParseError'

# some tools

def parts(text,indent):

    """ return a list of tuples (from, to, type) delimiting different
        parts in text; the whole text has to be indented by indent spaces
        * text must be TAB-free
        * type can be: def, class, \"\"\", import, from, <none of these>
        * this will only find statically defined objects -- using
          if's to do conditional defining breaks this method
    """

    # get parts regexp -- from cache if possible
    try:
        rx = rx_parts[indent]
    except:
        si = indent * ' '
        rs = '^'+si+'def \|^'+si+'class \|^'+si+'\"\"\"\|^'+ \
                 si+'import \|^'+si+'from \|^'+si+'__version__'#\|^'+si+'[^ \n]'
        rx = regex.compile(rs)
        rx_parts[indent] = rx
    l = [[0,0,'']]
    start = 0
#    print '-- breaking into parts using indent',indent,':'
    while 1:
#       print '-- looking at...\n'+text[start:start+50]
        t = rx.search(text,start)
        if t == -1: break
        type = rx.group(0)[indent:]
        if type[-1] == ' ': type = type[:-1]
        l[-1][1] = t # the last part ends here ...
        l.append([t,t,type]) # ... while the new one starts here
#       print '-- found part type >',type,'<:',rx.regs[0],':',text[t:t+20],'...'
        start = rx.regs[0][1]
    l[-1][1] = len(text)
    l = map(tuple,l)
#    print '** returning with parts:',`l`
    return l
    
def calc_bodyindent(text,start=0):

    """ calculate the bodyindent of the code starting at text[start:] """
    
    # this one works in most cases
    rx = rx_bodyindent
    if rx.search(text,start) != -1:
        a,b = rx.regs[1]
        return b-a
    else:
        # maybe there are no new lines left (e.g. at the end of a file)
        rx = rx_bodyindent_2
        if rx.search(text,start) != -1:
            a,b = rx.regs[1]
            return b-a
        else:
            # didn't think of this one... 
            print 'bodyindent failed for:\n--|'+text[start:]+'|-- why?'
            return 0

def subst(find,sub,text):

    """ substitute sub for every occurence of find in text """

    l = string.split(text,find)
    return string.joinfields(l,sub)

def fix_linebreaks(text):
    
    """ want to have Unix-style newlines everywhere (that is, no \r!) """

    text = subst('\r\n','\n',text)
    return subst('\r','\n',text)

def escape_long_strings(text):

    """ escape long string newlines so they don't disturb part-breaking
        * this only works, iff the long strings occur balanced everywhere !!!
    """

    l = string.split(text,'\"\"\"')
    for i in range(1,len(l),2):
        l[i] = subst('\n','\r',l[i])
    return string.joinfields(l,'\"\"\"')

def unescape_long_strings(text):

    """ inverse of the above function """

    l = string.split(text,'\"\"\"')
    for i in range(1,len(l),2):
        l[i] = subst('\r','\n',l[i])
    return string.joinfields(l,'\"\"\"')

def extract_doc_string(text):

    """ extract and unescape doc-string from long-string-part """

    l = string.split(text,'\"\"\"')
    s = subst('\r','\n',l[1])
    return s

def extract_version_string(text):

    """ parse a __version__ string statement """

    if rx_version.match(text) >= 0:
        return rx_version.group(1)
    return 'unspecified'

def fullname(doc):

    """ return the full name of a doc-class, that is the names of its
        owners and itself, concatenated with dots 
        -- the usual Python-fashion of naming things
    """

    t = doc.name
    while doc.owner is not None:
        doc = doc.owner
        t = doc.name + '.' + t
    return t

def get_parameters(paramstring,

                   split=string.split,strip=string.strip,
                   filter=filter,len=len,map=map):

    """ Returns a list of parameter strings.
    
        As a special feature, all parameters following an empty
        line are ignored in the list. This is useful for typical
        localization hacks like

        # func(a,b,c,
        # 
        #      str=str,find=string.find):
        #     ...
        
        The localizations are not shown in the generated docs.

        XXX Tuples in the parameter string are not supported !

    """
    lines = split(paramstring,'\n')
    parameters = []
    for i in range(len(lines)):
        line = strip(lines[i])
        if not line:
            break
        parameters[len(parameters):] = map(strip,split(line,','))
    return filter(len,parameters)

# the doc-classes

class doc_string:

    def __init__(self,text,owner=None):

        """ interpret text as a doc-string; instance-variables:
            * text    - original doc-string
            * owner   - owner-class of this object: this object is a member
                        of its super-object, e.g. a function
        """
        self.text = text

    def __str__(self):

        return self.text

    def as_HTML(self):

        """ return a HTML-Version of the doc-string; tries to interpret certain
            human formatting styles in HTML:
            * single leading characters occuring in the global list_markers
              turn into list items (the doc-string is enclosed in a <UL> ...
              </UL> tag)
            * lines of - or = turn into horizontal rules
            * empty lines serve as paragraph separators
            * the first paragraph is written in italics

            * emphasized writing of single words:
                 ' *bold* ' turns out bold
                 ' _underlined_ ' turns out underlined
                 ' /italics/ ' comes out in italics

            * lines starting or ending with a # are written monospaced
              and the '#' signaling this is deleted; example:

              # def unescape_long_strings(text):
              #   l = string.split(text,'\"\"\"')
              #   for i in range(1,len(l),2):
              #       l[i] = subst('\r','\n',l[i])
              #   return string.joinfields(l,'\"\"\"')

              The '#' indicates the start-of-line, that is only spaces
              after the comment mark turn up as spaces ! Or use:

              def unescape_long_strings(text):                  #
                l = string.split(text,'\"\"\"')         #
                for i in range(1,len(l),2):                     #
                    l[i] = subst('\r','\n',l[i])                #
                return string.joinfields(l,'\"\"\"')            #

              In this case all spaces on the left are layouted as such.
              The lines are concatenated into one XMP-field,
              so HTML-tags won't work in here -- e.g.

              # <BODY>
              #  <B> Works ! </B>
              # </BODY>

              gives you an easy-to-apply alternative to using the
              XMP-tag directly.

            * If you plan to put verbatim HTML-code inline then you can
              use this syntax \<I>This doesn't come out in italics\</I>, i.e.
              put a backslash in front of the tag. (The tag must not
              contain embedded '>' characters.)

            * detects mailto, http and ftp URLs and converts them to
              HTML links

            * Note: 'lines' in this context refer to everything between
              two newlines

            * The formatting demonstrated here won't show up in the
              HTML-output of this doc-string, so you'll have to look
              at the source code to find out how it works...
        """
        t = string.strip(self.text) + '\n'
        # bullets:
        t = regsub.gsub('^ *['+list_markers+'] ','<LI TYPE=BULLET> ',t)
        # rules
        t = regsub.gsub('^ *[-=]+\n','<HR>\n',t)
        # empty lines become paragraphs
        t = regsub.gsub('^ *\n','<P>\n',t)
        # guess first paragraph
        t = regsub.gsub('\`\([^<]*\)','<P><I>\\1</I></P>\n',t)
        # monospaced stuff, e.g. code
        t = regsub.gsub('^ *#\(.*\)\n','<XMP>\\1</XMP>\n',t)
        t = regsub.gsub('^\(.*\)#\n','<XMP>\\1</XMP>\n',t)
        t = regsub.gsub('</XMP>\n<XMP>','\n',t)
        # inline HTML
        t = regsub.gsub('\\\\<\(/*[A-Za-z][^>]*\)>','<TT>&lt;\\1&gt;</TT>',t)
        # emphasizing
        t = regsub.gsub(' \*\([^ \*]+\)\* ',' <B>\\1</B> ',t)
        t = regsub.gsub(' _\([^ _]+\)_ ',' <U>\\1</U> ',t)
        t = regsub.gsub(' /\([^ /]+\)/ ',' <I>\\1</I> ',t)
        # URL detection
        t = regsub.gsub('mailto:\([a-zA-Z0-9@.%\-]+\)',
                        'mailto:<A HREF="mailto:\\1">\\1</A>',t)
        t = regsub.gsub('http://\([a-zA-Z0-9@.%\-\/?&+=~]+\)',
                        '<A HREF="http://\\1">http://\\1</A>',t)
        t = regsub.gsub('ftp://\([a-zA-Z0-9@.%\-\/?&+=~]+\)',
                        '<A HREF="ftp://\\1">ftp://\\1</A>',t)

        t = '<P> %s </P>' % t

        return t

class doc_type:

    def __cmp__(self,other):

        return cmp(self.fullname,other.fullname)

class doc_class(doc_type):

    def __init__(self,text,sx,sy,owner=None):
    
        """ parse the text part [sx:sy] for a class definition and all its
            members; instance-variables:
            * text    - original code
            * slice   - the part of text where the class def is supposed to be
                        found
            * owner   - owner-class of this object: this object is a member
                        of its super-object, e.g. a module
            * indent  - indent of this def
            * name    - the class name
            * fullname - the full name of this class
            * baseclasses - list of names of baseclasses
            * doc     - doc-string as doc_string-object
            * methods - list of methods as doc_method-objects
            * classes - list of classes as doc_class-objects
            * bodyindent - indent of the definitions body
            * parts   - definition body, broken into parts
        """
        self.text = text
        self.slice = (sx,sy)
        self.owner = owner
        rx = rx_class
        start = rx.match(text,sx)
        if start < 0:
            # we've got a problem here
            print "-- can't find the class definition in:"
            print text[sx:sy]
            raise ParseError,"couldn't parse class definition"
        start = start + sx
        self.indent = len(rx.group(1))
        self.name = rx.group(2)
        if rx.group(3) is not None:
            self.baseclasses = string.split(rx.group(4),',')
        else:
            self.baseclasses = []
        self.doc = doc_string('',self)
        self.methods = []
        self.classes = []
        self.fullname = fullname(self)
        # calc body-indent
        self.bodyindent = calc_bodyindent(text,start)
        # break into parts
        self.parts = parts(text[start:sy],self.bodyindent)
        try:
            for x,y,type in self.parts:
                if  type == 'def': 
                    # got a method
                    self.methods.append(doc_method(text,start+x,start+y,self))
                elif type == 'class':
                    # got a class
                    self.classes.append(doc_class(text,start+x,start+y,self))
                elif type == '#':
                    # got a comment
                    pass
                elif type == '\"\"\"':
                    # got a doc-string
                    self.doc = doc_string(extract_doc_string(text[start+x:start+y]),self)
                else:
                    # something else
                    pass
        except ParseError,reason:
            print '-- ParseError:',reason
            print '-- was looking at:\n',text[start+x:start+y]
            print '-- Skipping the rest of this class (%s)'%self.fullname
        except regex.error,reason:
            print '-- RegexError:',reason
            print '-- was looking at:\n',text[start+x:start+y]
            print '-- Skipping the rest of this class (%s)'%self.fullname
        self.classes.sort()
        self.methods.sort()

    def as_HTML(self):

        """ give a HTML-version of the class and its members """

        output = '<LI TYPE=SQUARE><A NAME="'+self.fullname+'"><I>class</I>&nbsp;<B>'+self.name+'</B>&nbsp;('+ \
                 string.joinfields(self.baseclasses,',')+') <P><UL>'+\
                 self.doc.as_HTML() + '<P><FONT COLOR=EE9900 SIZE=-2>'+self.fullname+'</FONT></P></UL></P>'
        if self.classes:
            output = output + '<P>Classes: ' + \
                     string.join(
                         map(lambda m: \
                             '<A HREF="#'+m.fullname+'">'+m.name+'</A>',
                             self.classes),' : ') + \
                     '</P>'
        if self.methods:
            output = output + '<P>Methods: (' + \
                     string.join(
                         map(lambda m: \
                             '<A HREF="#'+m.fullname+'">'+m.name+'</A>',
                             self.methods),', ') + \
                     ')</P>'
        if self.classes:
            output = output + '<UL>'
            for m in self.classes:
                output = output + m.as_HTML()
            output = output + '</UL>'
        if self.methods:
            output = output + '<UL>'
            for m in self.methods:
                output = output + m.as_HTML()
            output = output + '</UL>'
        return output + '</LI>'

class doc_method(doc_type):

    def __init__(self,text,sx,sy,owner=None):
    
        """ parse the text part [sx:sy] for a method definition and all its
            members; instance-variables:
            * text    - original code
            * slice   - the part of text where the class def is supposed to be
                        found
            * owner   - owner-class of this object: this object is a member
                        of its super-object, e.g. a module
            * indent  - indent of this def
            * name    - the class name
            * fullname - the full name of this class
            * parameters - list of parameters needed for this method (without self)
            * doc     - doc-string as doc_string-object
            * functions - list of functions as doc_function-objects
            * classes - list of classes as doc_class-objects
            * bodyindent - indent of the definitions body
            * parts   - definition body, broken into parts
        """
        self.text = text
        self.slice = (sx,sy)
        self.owner = owner
        rx = rx_method
        start = rx.match(text,sx)
        if start < 0:
            # we've got a problem here
            print "-- can't find the method definition in:"
            print text[sx:sy]
            raise ParseError,"couldn't parse method definition"
        start = start + sx
        self.indent = len(rx.group(1))
        self.name = rx.group(2)
        self.parameters = get_parameters(rx.group(3))[1:]
        self.doc = doc_string('',self)
        self.functions = [] # don't think these are really needed...
        self.classes = []   # -"-
        self.fullname = fullname(self)
        # calc body-indent
        self.bodyindent = calc_bodyindent(text,start)
        # break into parts
        self.parts = parts(text[start:sy],self.bodyindent)
        try:
            for x,y,type in self.parts:
                if  type == 'def': 
                    # got a function
                    self.functions.append(doc_function(text,start+x,start+y,self))
                elif type == 'class':
                    # got a class
                    self.classes.append(doc_class(text,start+x,start+y,self))
                elif type == '#':
                    # got a comment
                    pass
                elif type == '\"\"\"':
                    # got a doc-string
                    self.doc = doc_string(extract_doc_string(text[start+x:start+y]),self)
                else:
                    # something else
                    pass
        except ParseError,reason:
            print '-- ParseError:',reason
            print '-- was looking at:\n',text[start+x:start+y]
            print '-- Skipping the rest of this method (%s)'%self.fullname
        except regex.error,reason:
            print '-- RegexError:',reason
            print '-- was looking at:\n',text[start+x:start+y]
            print '-- Skipping the rest of this method (%s)'%self.fullname
        self.classes.sort()
        self.functions.sort()

    def as_HTML(self):

        """ give a HTML-version of the method and its members """

        output = '<P><A NAME="'+self.fullname+'">-&nbsp;<I>method</I>&nbsp;<B>'+self.name+'</B>&nbsp;('+\
                 string.joinfields(self.parameters,', ')+') <P><UL>'+\
                 self.doc.as_HTML() + '<P><FONT COLOR=EE9900 SIZE=-2>'+self.fullname+'</FONT></P></UL></P>'
        if self.classes:
            output = output + '<P>Classes: ' + \
                     string.join(
                         map(lambda m: \
                             '<A HREF="#'+m.fullname+'">'+m.name+'</A>',
                             self.classes),' : ') + \
                     '</P>'
        if self.functions:
            output = output + '<P>Functions: (' + \
                     string.join(
                         map(lambda m: \
                             '<A HREF="#'+m.fullname+'">'+m.name+'</A>',
                             self.functions),', ') + \
                     ')</P>'
        if self.classes:
            output = output + '<UL>'
            for m in self.classes:
                output = output + m.as_HTML()
            output = output + '</UL>'
        if self.functions:
            output = output + '<UL>'
            for m in self.functions:
                output = output + m.as_HTML()
            output = output + '</UL>'
        return output + '</P>'

class doc_function(doc_type):

    def __init__(self,text,sx,sy,owner=None):
    
        """ parse the text part [sx:sy] for a method definition and all its
            members; instance-variables:
            * text    - original code
            * slice   - the part of text where the class def is supposed to be
                        found
            * owner   - owner-class of this object: this object is a member
                        of its super-object, e.g. a module
            * indent  - indent of this def
            * name    - the class name
            * fullname - the full name of this class
            * parameters - list of parameters needed for this function
            * doc     - doc-string as doc_string-object
            * functions - list of functions as doc_function-objects
            * classes - list of classes as doc_class-objects
            * bodyindent - indent of the definitions body
            * parts   - definition body, broken into parts
        """
        self.text = text
        self.slice = (sx,sy)
        self.owner = owner
        rx = rx_function
        start = rx.match(text[sx:sy])
        if start < 0:
            # we've got a problem here
            print "-- can't find the function definition in:"
            print text[sx:sy]
            raise ParseError,"couldn't parse function definition"
        start = start + sx
        self.indent = len(rx.group(1))
        self.name = rx.group(2)
        self.parameters = get_parameters(rx.group(3))
        self.doc = doc_string('',self)
        self.functions = []
        self.classes = []
        self.fullname = fullname(self)
        # calc body-indent
        self.bodyindent = calc_bodyindent(text,start)
        # break into parts
        self.parts = parts(text[start:sy],self.bodyindent)
#       print ' - function',self.parts,':\n',text[start:sy]
        try:
            for x,y,type in self.parts:
                if  type == 'def': 
                    # got a function
                    self.functions.append(doc_function(text,start+x,start+y,self))
                elif type == 'class':
                    # got a class
                    self.classes.append(doc_class(text,start+x,start+y,self))
                elif type == '#':
                    # got a comment
                    pass
                elif type == '\"\"\"':
                    # got a doc-string
                    self.doc = doc_string(extract_doc_string(text[start+x:start+y]),self)
                else:
                    # something else
                    pass
        except ParseError,reason:
            print '-- ParseError:',reason
            print '-- was looking at:\n',text[start+x:start+y]
            print '-- Skipping the rest of this function (%s)'%self.fullname
        except regex.error,reason:
            print '-- RegexError:',reason
            print '-- was looking at:\n',text[start+x:start+y]
            print '-- Skipping the rest of this function (%s)'%self.fullname
        self.classes.sort()
        self.functions.sort()

    def as_HTML(self):

        """ give a HTML-version of the function and its members """

        output = '<LI TYPE=CIRCLE><A NAME="'+self.fullname+'"><I>function</I>&nbsp;<B>'+self.name+'</B>&nbsp;('+\
                 string.join(self.parameters,', ')+') <P><UL>'+\
                 self.doc.as_HTML() + '<P><FONT COLOR=EE9900 SIZE=-2>'+self.fullname+'</FONT></P></UL></P>'
        if self.classes:
            output = output + '<P>Classes: ' + \
                     string.join(
                         map(lambda m: \
                             '<A HREF="#'+m.fullname+'">'+m.name+'</A>',
                             self.classes),' : ') + \
                     '</P>'
        if self.functions:
            output = output + '<P>Functions: (' + \
                     string.join(
                         map(lambda m: \
                             '<A HREF="#'+m.fullname+'">'+m.name+'</A>',
                             self.functions),', ') + \
                     ')</P>'
        if self.classes:
            output = output + '<UL>'
            for m in self.classes:
                output = output + m.as_HTML()
            output = output + '</UL>'
        if self.functions:
            output = output + '<UL>'
            for m in self.functions:
                output = output + m.as_HTML()
            output = output + '</UL>'
        return output + '</LI>'


class doc_module(doc_type):

    version = None

    def __init__(self,file,owner=None):

        """ parse the source code in file as Python module
            * owner   - owner-class of this object: this object is a member
                        of its super-object, e.g. a project
            * name    - the module name
            * doc     - doc-string as doc_string-object
            * functions - list of funtions as doc_function-objects
            * methods - list of methods as doc_method-objects
            * classes - list of classes as doc_class-objects
            * parts   - definition body, broken into parts
        """
        # read file, expand tabs, fix line breaks and long strings
        self.file = file
        self.text = open(self.file).read()
        self.text = string.expandtabs(self.text,tabsize)
        self.text = fix_linebreaks(self.text)
        self.text = escape_long_strings(self.text)
        # I need a linebreak at the file end to make things easier:
        if self.text[-1:] != '\n':
            self.text = self.text + '\n'
        self.name = os.path.split(file)[1][:-3] # strip path and .py
        self.owner = owner
        # break into parts
        self.parts = parts(self.text,0)
#       print ' - module',self.parts
        # parse
        self.functions = []
        self.classes = []
        self.doc = doc_string('',self)
        try:
            for x,y,type in self.parts:
                if  type == 'def': 
                    # got a function
                    self.functions.append(doc_function(self.text,x,y,self))
                elif type == 'class':
                    # got a class
                    self.classes.append(doc_class(self.text,x,y,self))
                elif type == '#':
                    # got a comment
                    pass
                elif type == '\"\"\"':
                    # got a doc-string
                    self.doc = doc_string(extract_doc_string(self.text[x:y]),self)
                elif type == '__version__':
                    # got a version-string
                    self.version = extract_version_string(self.text[x:y])
                else:
                    # something else
                    pass
        except ParseError,reason:
            print '-- ParseError:',reason
            print '-- was looking at:\n',self.text[x:y]
            print '-- Skipping the rest of this module (%s)'%file
        except regex.error,reason:
            print '-- RegexError:',reason
            print '-- was looking at:\n',self.text[x:y]
            print '-- Skipping the rest of this module (%s)'%file
        self.classes.sort()
        self.functions.sort()

    def as_HTML(self):

        """ give a HTML-version of the module and its members """

        output = '<A NAME="'+self.name+'"><HR SIZE=6><H2>Module: '+self.name+'</H2> <P><UL>'+\
                 self.doc.as_HTML()+'</UL></P>'
        if self.file[:2] == os.curdir + os.sep:
            filename = self.file[2:]
        else:
            filename = self.file
        if self.version:
            output = output + '<P>Version: <FONT COLOR=#FF0000>%s</FONT>' %\
                     self.version
#        output = output + '<P>Sourcecode: \
#                 <A HREF="%s" TARGET="source-window">plaintext</A>,\
#                 <A HREF="%s" TARGET="source-window">highlighted</A>' %\
#                 (hrefprefix+filename,highlighted % (hrefprefix+filename))
        output = output + '<DL>'
        if self.classes:
            output = output + '<DT><I>Classes:</I><DD>' + \
                     string.join(
                         map(lambda m: \
                             '<A HREF="#'+m.fullname+'">'+m.name+'</A>',
                             self.classes),' : ') + \
                     '</DD>'
        if self.functions:
            output = output + '<DT><I>Functions:</I><DD>' + \
                     string.join(
                         map(lambda m: \
                             '<A HREF="#'+m.fullname+'">'+m.name+'</A>',
                             self.functions),' : ') + \
                     '</DD>'
        output = output + '</DL>'
        if self.classes:
            output = output + '<HR><UL>'
            for m in self.classes:
                output = output + m.as_HTML()
            output = output + '</UL>'
        if self.functions:
            output = output + '<HR><UL>'
            for m in self.functions:
                output = output + m.as_HTML()
            output = output + '</UL>'
        return output


class doc_project:

    def __init__(self,path,name='test'):

        """ find all Python-files in path and parse them via doc_module
            * name    - project name
            * path    - pathname
            * files   - filenames found
            * modules - list of modules as doc_module-objects
        """
        self.name = name
        self.path = path
        self.files = filter(lambda f: f[-3:]=='.py', os.listdir(path))
        self.files.sort()
        self.modules = []
        for f in self.files:
            print ' scanning',f
            self.modules.append(doc_module(os.path.join(path,f)))

    def make_HTML(self):

        """ create a HTML-version of the project and its members using
            FRAMES and three files: the frameset-file, the module index and the
            content file
        """

        print 'generating files...'

        # set filenames
        self.main = self.name+'.html'
        self.index = self.name+'.idx.html'
        self.content = self.name+'.docs.html'

        # open files
        main = open(self.main,'w')
        index = open(self.index,'w')
        content = open(self.content,'w')

        # write main-file
        main.write("""
      <HTML>
      <HEAD>
      <TITLE>Docs::Project::%s</TITLE>
      <!--Created by the Python Doc-Tool V%s on %s-->
      <META NAME="KEYWORDS" CONTENT="%s, doc, documentation, python">
      </HEAD>
      <FRAMESET COLS="200,*">
      <FRAME NAME="index" SRC="%s" MARGINHEIGHT=0 MARGINWIDTH=0>
      <FRAME NAME="content" SRC="%s" MARGINHEIGHT=0 MARGINWIDTH=0>
      </FRAMESET>
      </HTML>
        """ % (self.name, __version__, time.ctime(time.time()),
        self.name, hrefprefix+self.index, hrefprefix+self.content))
        main.close()

        # make index-file
        print '',self.index
        output = """
                    <HTML>
                    <HEAD>
                    <TITLE>DocIndex::Project::%s</TITLE>
                    <META NAME="KEYWORDS" CONTENT="%s, index, documentation, python">
                    </HEAD>
                    <BODY BGCOLOR=#FFFFFF>
                 """ % (self.name, self.name)
        output = output + '<HR SIZE=7><H2>Project:&nbsp;'+self.name+'</H2>'
        for m in self.modules:
            output = output + '<B>Module&nbsp;<A HREF="'+hrefprefix+self.content+\
                     '#'+m.name+'" TARGET="content">'+m.name+'</A></B><BR>'
            if m.classes:
                output = output + '<UL><I>Classes</I><BR><BR>'
                for c in m.classes:
                    output = output + '<LI TYPE=DISC>' +\
                             '<A HREF="'+hrefprefix+self.content+\
                             '#'+c.fullname+'" TARGET="content">'+c.name+'</A><BR>'
                    if c.methods != []:
                        output = output + '<FONT SIZE=-1>'
                        for me in c.methods:
                            output = output + '-&nbsp;<A HREF="'+hrefprefix+self.content+\
                                     '#'+me.fullname+'" TARGET="content">'+me.name+'</A><BR>'
                        output = output + '</FONT>'
                    output = output + '<BR>'
                output = output + '</UL>'
            if m.functions:
                output = output + '<UL><I>Functions</I><BR><BR>'
                for f in m.functions:
                    output = output + '<LI TYPE=DISC>' +\
                             '<A HREF="'+hrefprefix+self.content+\
                             '#'+f.fullname+'" TARGET="content">'+f.name+'</A>'
                output = output + '</UL>'

        output = output + '</BODY></HTML>'
        index.write(output)
        index.close()
        
        # make content-file
        print '',self.content
        output = """
                    <HTML>
                    <HEAD>
                    <TITLE>Docs::Project::%s</TITLE
                    <META NAME="KEYWORDS" CONTENT="%s, docs, documentation, python, doc-tool">
                    </HEAD>
                    <BODY BGCOLOR=#FFFFFF>
                 """ % (self.name,self.name)
        for m in self.modules:
            output = output + m.as_HTML()
        output = output + "<HR><P ALIGN=CENTER><FONT SIZE=-1>Created by Doc-Tool V"+__version__+\
                 " on "+time.ctime(time.time())+"</FONT></P>"
        output = output + '</BODY></HTML>'
        content.write(output)
        content.close()

# simple interface:

def main():

    global hrefprefix

    print 'Doc-Tool V'+__version__+' (c) Marc-Andre Lemburg; mailto:mal@lemburg.com'
    print
    if len(sys.argv) < 3:
        print 'Syntax:',sys.argv[0],'project-name project-dir [HREF-prefix]'
        print
        print 'The tool will create HTML-files with prefix <project-name> containing'
        print 'the doc-strings of the found Python-files in a structured form.'
        print 'The links in these files will be prepended with HREF-prefix, if'
        print 'given, to simplify the upload to a website.'
        print
        print 'Enjoy !'
        sys.exit()
    project,dir = sys.argv[1:3]
    print 'Working on project:',project
    print ' project directory:',dir
    print
    print 'Creating files...'
    if len(sys.argv) >= 4:
        hrefprefix = sys.argv[3]
    else:
        hrefprefix = ''
    p = doc_project(dir,project)
    p.make_HTML()
    print 'Done. Point your browser at',hrefprefix+sys.argv[1]+'.html'

if __name__ == '__main__':
    main()
    
