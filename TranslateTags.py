##############################################################################
#    Copyright (C) 2001, 2002, 2003 Lalo Martins <lalo@laranja.org>,
#                  and Contributors

#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307, USA
__version__ = '''
$Id: TranslateTags.py,v 1.2 2004/02/03 22:14:42 tiran Exp $
'''.strip()

from utils import log
from DocumentTemplate.DT_String import String
from DocumentTemplate.DT_Util import parse_params
import string, random, Globals, os, glob, zLOG
from DocumentTemplate import DT_Var, DT_Util

def get(d, k, f):
    try:
        return d[k]
    except KeyError:
        return f

class TranslateTag:
    """DTML tag equivalent to ZPT's i18n:translate
    """

    # this is the minimal amount of meta-data needed by a DTML Tag.
    name='translate'
    blockContinuations=()
    _msgid = None
    _domain = None

    def __init__(self, blocks):
        self.blocks=blocks
        tname, args, section = blocks[0]
        self.__name__="%s %s" % (tname, args)
        args = parse_params(args, msgid='', domain='')
        if args.has_key('msgid'): self._msgid=args['msgid']
        elif args.has_key(''): self._msgid=args['']
        if args.has_key('domain'): self._domain=args['domain']

    def render(self, md):
        r=[]
        for tname, args, section in self.blocks:
            __traceback_info__=tname
            r.append(section(None, md))

        if r:
            if len(r) > 1: r = "(%s)\n" % join(r,' ')
            else: r = r[0]
        else:
            r = ''

        msgid = self._msgid or r
        domain = self._domain or get(md, 'i18n-domain', 'DTML')

        return translate(domain, msgid, context=md['REQUEST'], default=r) + '\n'

    __call__=render

def initialize():
    global translate
    from Products.PlacelessTranslationService import translate

    for c in (TranslateTag,):
        String.commands[c.name] = c
