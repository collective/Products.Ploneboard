
## ===========================================================================
##  NAME:       exif
##  TYPE:       python script
##  CONTENT:    library for parsing EXIF headers
## ===========================================================================
##  AUTHORS:    rft     Robert F. Tobler
## ===========================================================================
##  HISTORY:
##  24-Sep-02 20:00:00  ts	added maker notes for canon and olympus
##  23-Sep-02 18:00:00	ts	imported exiftags.py
##  10-Aug-01 11:14:20  rft     last modification
##  09-Aug-01 16:51:05  rft     created
## ===========================================================================

import string

ASCII = 0
BINARY = 1

global verbose_opt
verbose_opt = 0

## ---------------------------------------------------------------------------
##  'Tiff'
##  	This class provides the Exif header as a file-like object and hides
##  	endian-specific data access.
## ---------------------------------------------------------------------------

class Tiff:
    def __init__(self, data, file = None):
        self.data = data
        self.file = file
        self.endpos = len(data)
        self.pos = 0
        if self.data[0:2] == "MM":
            self.S0 = 1 ; self.S1 = 0
            self.L0 = 3 ; self.L1 = 2 ; self.L2 = 1 ; self.L3 = 0
        else:
            self.S0 = 0 ; self.S1 = 1
            self.L0 = 0 ; self.L1 = 1 ; self.L2 = 2 ; self.L3 = 3

    def seek(self, pos):
        self.pos = pos
        if self.pos > self.endpos:
            self.data += self.file.read( self.endpos - self.pos )
        
    def tell(self):
        return self.pos

    def read(self, len):
        old_pos = self.pos
        self.pos = self.pos + len
        if self.pos > self.endpos:
            self.data += self.file.read( self.endpos - self.pos )
        return self.data[old_pos:self.pos]

    def byte(self, signed = 0):
    	pos = self.pos
        self.pos = pos + 1
        if self.pos > self.endpos:
            self.data += self.file.read( self.endpos - self.pos )
        hi = ord(self.data[pos])
        if hi > 127 and signed: hi = hi - 256
        return hi

    def short(self, signed = 0):
        pos = self.pos
    	self.pos = pos + 2
        if self.pos > self.endpos:
            self.data += self.file.read( self.endpos - self.pos )
    	hi = ord(self.data[pos+self.S1])
    	if hi > 127 and signed: hi = hi - 256
    	shortval = (hi<<8)|ord(self.data[pos+self.S0])
    	# print "shortval:", shortval, "tipo_shortval:", type(shortval)
    	return shortval

    def long(self, signed = 0):
        pos = self.pos
        self.pos = pos + 4
        if self.pos > self.endpos:
            self.data += self.file.read( self.endpos - self.pos )
        hi = ord(self.data[pos+self.L3])
        if hi > 127 and not signed: hi = long(hi)
        return (hi<<24) | (ord(self.data[pos+self.L2])<<16) \
            | (ord(self.data[pos+self.L1])<<8) | ord(self.data[pos+self.L0])

## ---------------------------------------------------------------------------
##  'Type', 'Type...'
##  	A small hierarchy of objects that knows how to read each type of tag
##  	field from a tiff file, and how to pretty-print each type of tag.
##
##  	The method 'read' is used to read a tag with a given count from the
##  	supplied tiff file.
##
##  	The method 'str_table' is used to pretty-print the value table of a
##  	tag if no special format for this tag is present.
## ---------------------------------------------------------------------------

class Type:
    def str_table(self, table):
        result = []
        for val in table: result.append(self.str_value(val))
        return string.join(result, ", ")
    def str_value(self, val):
        return str(val)

class TypeByte(Type):
    def __init__(self): self.name = "BYTE" ; self.len = 1
    def read(self, tiff, count):
    	table = []
        for i in range(0, count): table.append(tiff.byte())
        return table

class TypeAscii:
    def __init__(self): self.name = "ASCII" ; self.len = 1
    def read(self, tiff, count):
        return tiff.read(count-1)
    def str_table(self, table):
        return string.strip(table)

class TypeShort(Type):
    def __init__(self): self.name = "SHORT" ; self.len = 2
    def read(self, tiff, count):
        table = []
        for i in range(0, count): table.append(tiff.short())
        return table

class TypeLong(Type):
    def __init__(self): self.name = "LONG" ; self.len = 4
    def read(self, tiff, count):
	table = []
	for i in range(0, count): table.append(tiff.long())
	return table

class TypeRatio(Type):
    def __init__(self): self.name = "RATIO" ; self.len = 8
    def read(self, tiff, count):
	table = []
	for i in range(0, count): table.append((tiff.long(), tiff.long()))
	return table
    def str_value(self, val):
	return "%d/%d" %(val[0], val[1])

class TypeSByte(Type):
    def __init__(self): self.name = "SBYTE" ; self.len = 1
    def read(self, tiff, count):
    	table = []
	for i in range(0, count): table.append(tiff.byte(signed=1))
	return table

class TypeUndef(TypeByte):
    def __init__(self): self.name = "UNDEF" ; self.len = 1
    def read(self, tiff, count):
        return tiff.read(count)
    def str_table(self, table):
        result = map( lambda x: str(ord(x)), table )
        # this next line is somehow much more efficient than using str()
    	return '[ ' + string.join( result, ',' ) + ' ]'

class TypeSShort(Type):
    def __init__(self): self.name = "SSHORT" ; self.len = 2
    def read(self, tiff, count):
	table = []
	for i in range(0, count): table.append(tiff.short(signed=1))
	return table

class TypeSLong(Type):
    def __init__(self): self.name = "SLONG" ; self.len = 4
    def read(self, tiff, count):
	table = []
	for i in range(0, count): table.append(tiff.short(signed=1))
	return table

class TypeSRatio(TypeRatio):
    def __init__(self): self.name = "SRATIO" ; self.len = 8
    def read(self, tiff, count):
	table = []
	for i in range(0, count):
	    table.append((tiff.long(signed=1), tiff.long(signed=1)))
	return table

class TypeFloat:
    def __init__(self): self.name = "FLOAT" ; self.len = 4
    def read(self, tiff, count):
	return tiff.read(4 * count)

class TypeDouble:
    def __init__(self): self.name = "DOUBLE" ; self.len = 8
    def read(self, tiff, count):
	return tiff.read(8 * count)

TYPE_MAP = {
	1:	TypeByte(),
	2:	TypeAscii(),
	3:	TypeShort(),
	4:	TypeLong(),
	5:	TypeRatio(),
	6:	TypeSByte(),
	7:	TypeUndef(),
	8:	TypeSShort(),
	9:	TypeSLong(),
	10:	TypeSRatio(),
	11:	TypeFloat(),
	12:	TypeDouble(),
}

## ---------------------------------------------------------------------------
##  'Tag'
##  	A tag knows about its name and an optional format.
## ---------------------------------------------------------------------------

class Tag:
    def __init__(self, name, format = None):
	self.name = name
	self.format = format

## ---------------------------------------------------------------------------
##  'Format', 'Format...'
##  	A small hierarchy of objects that provide special formats for certain
##  	tags in the EXIF standard.
##
##  	The method 'str_table' is used to pretty-print the value table of a
##  	tag. It gets the table of tags that have already been parsed as a
##  	parameter in order to handle vendor specific extensions.
## ---------------------------------------------------------------------------

class Format:
    def str_table(self, table, value_map):
	result = []
	for val in table: result.append(self.str_value(val))
	return string.join(result, ", ")

class FormatMap:
    def __init__(self, map, make_ext = {}):
	self.map = map
	self.make_ext = make_ext
    def str_table(self, table, value_map):
	if len(table) == 1:
	    key = table[0]
	else:
	    key = table
	value = self.map.get(key)
	if not value:
	    make = value_map.get("Make")
	    if make: value = self.make_ext.get(make,{}).get(key)
	    if not value: value = `key`
	return value

class FormatTable:
    def __init__(self, table):
	self.table = table

    def str_table(self, table, value_map):
	for i in self.table.keys():
	    v = [table[i]]
	    tag = self.table.get(i)
	    if tag.format:
		value_map[tag.name] = tag.format.str_table(v,value_map)
	    else:
	    	value_map[tag.name] = v[0]
	return None

class FormatRatioAsFloat(Format):
    def str_value(self, val):
	if val[1] == 0: return "0.0"
	return "%g" % (val[0]/float(val[1]))

class FormatRatioAsBias(Format):
    def str_value(self, val):
	if val[1] == 0: return "0.0"
	if val[0] > 0: return "+%3.1f" % (val[0]/float(val[1]))
	if val[0] < 0: return "-%3.1f" % (-val[0]/float(val[1]))
	return "0.0"

def format_time(t):
    if t > 0.5: return "%g" % t
    if t > 0.1: return "1/%g" % (0.1*int(10/t+0.5))
    return "1/%d" % int(1/t+0.5)

class FormatRatioAsTime(Format):
    def str_value(self, val):
	if val[1] == 0: return "0.0"
    	return format_time(val[0]/float(val[1]))

class FormatRatioAsApexTime(Format):
    def str_value(self, val):
	if val[1] == 0: return "0.0"
	return format_time(pow(0.5, val[0]/float(val[1])))

class FormatRatioAsString(Format):
    def str_value(self,val):
	if val == 0:
	    return ''
	else:
	    return str(val)

    def str_table(self, table, value_map):
#        result = []
#        for val in table: result.append(self.str_value(val))
        return str(table)  #string.join(result, ", ")


## ---------------------------------------------------------------------------
##  'MakerNote...'
##  	This currently only parses Nikon E990, and Nikon E995 MakerNote tags.
##  	Additional objects with a 'parse' function can be placed here to add
##  	support for other cameras. This function adds the pretty-printed
##  	information in the MakerNote to the 'value_map' that is supplied.
## ---------------------------------------------------------------------------

class MakerNoteTags:
    def __init__(self, tag_map):
        self.tag_map = tag_map
    def parse(self, tiff, mode, tag_len, value_map):
    	num_entries = tiff.short()
    	if verbose_opt: print num_entries, 'tags'
    	for field in range(0, num_entries):
    	    parse_tag(tiff, mode, value_map, self.tag_map)
   
from exiftags import * 
NIKON_99x_MAKERNOTE = MakerNoteTags(NIKON_99x_MAKERNOTE_TAG_MAP)
NIKON_D1H_MAKERNOTE = MakerNoteTags(NIKON_D1H_MAKERNOTE_TAG_MAP)
CANON_IXUS_MAKERNOTE = MakerNoteTags(CANON_IXUS_MAKERNOTE_TAG_MAP) 

## ---------------------------------------------------------------------------
##  'MAKERNOTE_MAP'
##  	Interpretation of the MakerNote tag indexed by 'Make', 'Model' pairs.
## ---------------------------------------------------------------------------

MAKERNOTE_MAP = {
	('NIKON', 'E990'):  NIKON_99x_MAKERNOTE,
	('NIKON', 'E995'):  NIKON_99x_MAKERNOTE,
	('NIKON CORPORATION', 'NIKON D1H'):  NIKON_D1H_MAKERNOTE,
	('Canon', 'Canon DIGITAL IXUS v'): CANON_IXUS_MAKERNOTE,
}

def parse_tag(tiff, mode, value_map, tag_map):
    tag_id = tiff.short()
    type_no = tiff.short()
    count = tiff.long()

    tag = tag_map.get(tag_id)
    if not tag: tag = Tag("Tag0x%x" % tag_id)

    type = TYPE_MAP[type_no]

    if verbose_opt:
	print "%30s:" % tag.name,
	if verbose_opt > 1: print "%6s %3d" % (type.name, count),
    pos = tiff.tell()
    tag_len = type.len * count
    if tag_len > 4:
	tag_offset = tiff.long()
	tiff.seek(tag_offset)
	if verbose_opt > 1: print "@%03x :" % tag_offset,
    else:
	if verbose_opt > 1: print "     :",
    
    if tag.name == 'MakerNote':
        makernote = MAKERNOTE_MAP.get((value_map['Make'],value_map['Model']))
        if makernote:
            makernote.parse(tiff, mode, tag_len, value_map)
            value_table = None
        else:
            value_table = type.read(tiff, count)
    else:
        value_table = type.read(tiff, count)

    if value_table:
    	if mode == ASCII:
	    if tag.format:
		val = tag.format.str_table(value_table, value_map)
	    else:
		val = type.str_table(value_table)
	else:
	    val = value_table
	value_map[tag.name] = val
	if verbose_opt:
	    if value_map.has_key(tag.name): print val,
	    print
    tiff.seek(pos+4)

def parse_ifd(tiff, mode, offset, value_map):
    tiff.seek(offset)
    num_entries = tiff.short()
    if verbose_opt > 1:
	print "%30s:        %3d @%03x" % ("IFD", num_entries, offset)
    for field in range(0, num_entries):
	parse_tag(tiff, mode, value_map, TAG_MAP)
    offset = tiff.long()
    return offset

def parse_tiff(tiff, mode):
    value_map = {}
    order = tiff.read(2)
    if tiff.short() == 42:
	offset = tiff.long()
	while offset > 0:
	    offset = parse_ifd(tiff, mode, offset, value_map)

	    if offset == 0: 	    	    	    # special handling to get
		if value_map.has_key('ExifOffset'): # next EXIF IFD
	    	    offset = value_map['ExifOffset']
		    if mode == ASCII:
			offset = int(offset)
		    else:
			offset = offset[0]
		    del value_map['ExifOffset']
    return value_map


def parse_tiff_fortiff(tiff, mode):

    """Parse a real tiff file, not an EXIF tiff file."""

    value_map = {}
    order = tiff.read(2)
    if tiff.short() == 42:
        offset = tiff.long()

        # build a list of small tags, we don't want to parse the huge stuff
        stags = []
        while offset > 0:
            tiff.seek(offset)
            num_entries = tiff.short()
    
            if verbose_opt > 1:
                print "%30s:        %3d @%03x" % ("IFD", num_entries, offset)
            
            for field in range(0, num_entries):
                pos = tiff.tell()
                
                tag_id = tiff.short()
                type_no = tiff.short()
                length = tiff.long()
                valoff = tiff.long()
                #print TAG_MAP[ tag_id ].name, length

                if tag_id == 0x8769:
		    if mode == ASCII:
			valoff = int(valoff)
		    else:
			valoff = valoff[0]
                    stags += [ (tag_id, valoff) ]

                elif length < 1024:
                    stags += [ (tag_id, pos) ]

            offset = tiff.long()

            # IMPORTANT: we read the 0st ifd only for this.
            # The second is reserved for the thumbnail, whatever is in there
            # we ignore.
            break
        
        for p in stags:
            (tag_id, pos) = p
                
            if tag_id == 0x8769:
                parse_ifd(tiff, mode, pos, value_map)
            else:
                tiff.seek( pos )
                parse_tag(tiff, mode, value_map, TAG_MAP)

    return value_map


## ---------------------------------------------------------------------------
##  'parse'
##  	This is the function for parsing the EXIF structure in a file given
##  	the path of the file.
##  	The function returns a map which contains all the exif tags that
##  	were found, indexed by the name of the tag. The value of each tag
##  	is already converted to a nicely formatted string.
## ---------------------------------------------------------------------------
# def parse(pathname, verbose = 0, mode = 0):
def parse(file, verbose = 0, mode = 0):
    """ Parses the file and extracts the data as a dictionary"""
    
    global verbose_opt
    verbose_opt = verbose
    try:
        # file = open(path_name, "rb")
        file = file
        data = file.read(12)
        if data[0:4] == '\377\330\377\341' and data[6:10] == 'Exif':
            # JPEG
            length = ord(data[4]) * 256 + ord(data[5])
            if verbose > 1:
                print '%30s:  %d' % ("EXIF header length",length)
            tiff = Tiff(file.read(length-8))
            value_map = parse_tiff(tiff, mode)
        elif data[0:2] in [ 'II', 'MM' ] and ord(data[2]) == 42:
                # Tiff
                tiff = Tiff(data,file)
                tiff.seek(0)
                value_map = parse_tiff_fortiff(tiff, mode)
        else:
            print "Some other file format, sorry:", data[6:10]
            # Some other file format, sorry.
            value_map = {}
            
        file.seek(0)
        # file.close()
    except IOError:
        value_map = {}

    return value_map

## ===========================================================================
#
#
# The following methods are meant to be used by the 
# PhotoIptcExif ProductExtension to Photo Product v.1.2.3.
#   
#

def nparse(app1data, verbose = 0, mode=0):
    """ Helper. Parses Jpeg files and extracts the data as a dictionary"""
    global verbose_opt
    verbose_opt = verbose
    tiff = Tiff(app1data[6:])
    value_map = parse_tiff(tiff, mode)
    return value_map


def mparse(file, verbose = 0, mode=0):
    """ Helper. Parses Tiff files and extracts the data as a dictionary"""
    global verbose_opt
    verbose_opt = verbose
    try:
        file.seek(0)
        data = file.read(12)
        tiff = Tiff(data,file)
        tiff.seek(0)
        value_map = parse_tiff_fortiff(tiff, mode)          
        # file.close()
    except IOError:
        value_map = {}

    return value_map








