#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
# Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>
#
# Changed by Christian 'Tiran' Heimes <ch@comlounge.net> for the placeless
# translation service (PTS) of zope

"""Generate binary message catalog from textual translation description.

This program converts a textual Uniforum-style message catalog (.po file) into
a binary GNU catalog (.mo file).  This is essentially the same function as the
GNU msgfmt program, however, it is a simpler implementation.

This file was taken from Python-2.3.2/Tools/i18n and altered in several ways. 
Now you can simply use it from another python module:

  from msgfmt import Msgfmt
  mo = Msgfmt(po).get()

where po is path to a po file as string, an opened po file ready for reading or
a list of strings (readlines of a po file) and mo is the compiled mo
file as binary string.

Exceptions:

  * IOError if the file couldn't be read
  
  * msgfmt.PoSyntaxError if the po file has syntax errors

"""
import sys, os
import struct
import array
from types import FileType, StringType, ListType
from cStringIO import StringIO

__version__ = "1.1pts"


try:
    True
except NameError:
    True=1
    False=0

class PoSyntaxError(Exception):
    """ Syntax error in a po file """
    def __init__(self, lno):
        self.lno = lno
        
    def __str__(self):
        return 'Po file syntax error on line %d' % self.lno

class Msgfmt:
    """ """
    def __init__(self, po):
        self.po = po
        self.messages = {}

    def readPoData(self):
        """ read po data from self.po and store it in self.poLines """
        output = []
        if type(self.po) is FileType:
            self.po.seek(0)
            output = self.po.readlines()
        if type(self.po) is ListType:
            output = self.po
        if type(self.po) is StringType:
            output = open(self.po, 'r').readlines()
        if not output:
            raise ValueError, "self.po is invalid! %s" % type(self.po)
        return output

    def add(self, id, str, fuzzy):
        "Add a non-fuzzy translation to the dictionary."
        if not fuzzy and str:
            self.messages[id] = str

    def generate(self):
        "Return the generated output."
        keys = self.messages.keys()
        # the keys are sorted in the .mo file
        keys.sort()
        offsets = []
        ids = strs = ''
        for id in keys:
            # For each string, we need size and file offset.  Each string is NUL
            # terminated; the NUL does not count into the size.
            offsets.append((len(ids), len(id), len(strs), len(self.messages[id])))
            ids += id + '\0'
            strs += self.messages[id] + '\0'
        output = ''
        # The header is 7 32-bit unsigned integers.  We don't use hash tables, so
        # the keys start right after the index tables.
        # translated string.
        keystart = 7*4+16*len(keys)
        # and the values start after the keys
        valuestart = keystart + len(ids)
        koffsets = []
        voffsets = []
        # The string table first has the list of keys, then the list of values.
        # Each entry has first the size of the string, then the file offset.
        for o1, l1, o2, l2 in offsets:
            koffsets += [l1, o1+keystart]
            voffsets += [l2, o2+valuestart]
        offsets = koffsets + voffsets
        output = struct.pack("Iiiiiii",
                             0x950412deL,       # Magic
                             0,                 # Version
                             len(keys),         # # of entries
                             7*4,               # start of key index
                             7*4+len(keys)*8,   # start of value index
                             0, 0)              # size and offset of hash table
        output += array.array("i", offsets).tostring()
        output += ids
        output += strs
        return output


    def get(self):
        """ """
        ID = 1
        STR = 2

        section = None
        fuzzy = 0
        
        lines = self.readPoData()

        # Parse the catalog
        lno = 0
        #import pdb; pdb.set_trace()
        for l in lines:
            lno += 1
            # If we get a comment line after a msgstr or a line starting with 
            # msgid, this is a new entry
            # XXX: l.startswith('msgid') is needed because not all msgid/msgstr
            # pairs in the plone pos have a leading comment
            if (l[0] == '#' or l.startswith('msgid')) and section == STR:
                self.add(msgid, msgstr, fuzzy)
                section = None
                fuzzy = 0
            # Record a fuzzy mark
            if l[:2] == '#,' and l.find('fuzzy'):
                fuzzy = 1
            # Skip comments
            if l[0] == '#':
                continue
            # Now we are in a msgid section, output previous section
            if l.startswith('msgid'):
                section = ID
                l = l[5:]
                msgid = msgstr = ''
            # Now we are in a msgstr section
            elif l.startswith('msgstr'):
                section = STR
                l = l[6:]
            # Skip empty lines
            l = l.strip()
            if not l:
                continue
            # XXX: Does this always follow Python escape semantics?
            l = eval(l)
            if section == ID:
                msgid += l
            elif section == STR:
                msgstr += l
            else:
                raise PoSyntaxError(lno)

        # Add last entry
        if section == STR:
            self.add(msgid, msgstr, fuzzy)

        # Compute output
        return self.generate()

    def getAsFile(self):
        return StringIO(self.get())

    def __call__(self):
        return self.getAsFile()


def main(pofile='/var/lib/zope/plone/Products/PlacelessTranslationService/plone-nl.po'):
    from gettext import GNUTranslations
    from cStringIO import StringIO
    import os
    #import locale
    #locale.setlocale(locale.LC_ALL, 'de_DE@euro')
    po = pofile
    mo = Msgfmt(po)
    
    moFile = mo.getAsFile()
    tro = None
    tro = GNUTranslations(moFile)
    return dir(tro)

if __name__ == '__main__':
    print main()
